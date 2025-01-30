import uuid
from datetime import date
from typing import Dict, List, Tuple

from django.db.models import Q

from ..models import Organization, Person, SanctionedEntity
from .COUNTRY import COUNTRY_RISK_LEVELS


class RiskScorer:
    RISK_WEIGHTS = {
        'sanctions_match': 0.40,
        'pep': 0.10,
        'geography': 0.20,
        'adverse_media': 0.20,
        'transactions': 0.10
    }
    COUNTRY_RISK_LEVELS = COUNTRY_RISK_LEVELS

    
    GEOGRAPHIC_RISK_SCORES = {
        'HIGH_RISK': 1.0,
        'MEDIUM_RISK': 0.5,
        'LOW_RISK': 0.1,
        'DEFAULT': 0
    }


    def __init__(self, entity_data: Dict, transaction_data: Dict = None):
        self.entity_data = entity_data
        self.transaction_data = transaction_data or {}
        self.reasons: List[str] = []
        
    def get_entity_id(self) -> str:
        """
        Helper method to find and return entity ID from database.
        Handles JSON array fields for person attributes.
        """
        # Try to find matching person first
        person_query = Person.objects.all()
        
        # Name is stored as a JSON array, so we need to check if the name exists in the array
        if self.entity_data.get('name'):
            person_query = person_query.filter(name__contains=[self.entity_data['name']])
        
        if self.entity_data.get('date_of_birth'):
            birth_date = self.entity_data['date_of_birth']
            person_query = person_query.filter(birthDate__contains=[str(birth_date)])

        # Add nationality filter if provided (stored as JSON array)
        if self.entity_data.get('nationality'):
            person_query = person_query.filter(nationality__contains=[self.entity_data['nationality']])
        
        # Get the first matching person if any
        person_match = person_query.first()
        if person_match:
            return str(person_match.id)
        
        # If no person found, try organization
        org_query = Organization.objects.all()
        
        if self.entity_data.get('name'):
            org_query = org_query.filter(name__contains=[self.entity_data['name']])
            
        if self.entity_data.get('id_number'):
            org_query = org_query.filter(registrationNumber__contains=[self.entity_data['id_number']])
        
        org_match = org_query.first()
        if org_match:
            return str(org_match.id)
        
        # If no match found, generate a new UUID
        return str(uuid.uuid4())
                
    def check_sanctions_match(self) -> float:
        """Check if entity matches any sanctions lists."""
        name = self.entity_data['name']
        
        # Check in SanctionedEntity and related models
        sanctions_match = SanctionedEntity.objects.filter(
            target=True
        ).filter(
            Q(person__name__icontains=name) |
            Q(organization__name__icontains=name)
        ).exists()
        
        if sanctions_match:
            self.reasons.append("Entity found on sanctions list")
            return 1.0
        return 0.0

    def check_pep_status(self) -> float:
        """Check if entity is a PEP."""
        pep_match = Person.objects.filter(
            political__isnull=False,
            name__contains=self.entity_data['name']
        ).exists()
        
        if pep_match:
            self.reasons.append("Entity identified as PEP")
            return 1.0
        return 0.0

    def assess_geographic_risk(self) -> float:
        """
        Assess risk based on geography using FATF standards and other international guidelines.
        Returns a risk score between 0.0 and 1.0.
        """
        country = self.entity_data['nationality']

        # Determine country risk level
        if country in self.COUNTRY_RISK_LEVELS['HIGH_RISK']:
            self.reasons.append(f"High-risk jurisdiction: {country}")
            return self.GEOGRAPHIC_RISK_SCORES['HIGH_RISK']
            
        if country in self.COUNTRY_RISK_LEVELS['MEDIUM_RISK']:
            self.reasons.append(f"Medium-risk jurisdiction: {country}")
            return self.GEOGRAPHIC_RISK_SCORES['MEDIUM_RISK']
            
        if country in self.COUNTRY_RISK_LEVELS['LOW_RISK']:
            return self.GEOGRAPHIC_RISK_SCORES['LOW_RISK']
        
        # For unlisted countries, add a reason for transparency
        self.reasons.append(f"Country {country} not found in risk classification list - using default risk score")
        return self.GEOGRAPHIC_RISK_SCORES['DEFAULT']

    def check_adverse_media(self) -> float:
        """Check for adverse media mentions."""
        has_adverse_media = Person.objects.filter(
            name__contains=self.entity_data['name'],
            notes__isnull=False
        )
        
        if has_adverse_media.exists():
            person = has_adverse_media.first()
            self.reasons.append(f"Adverse media mentions found: ({person.notes[0]})")
            return 1.0
        return 0.0

    def assess_transaction_risk(self) -> float:
        """Assess risk based on transaction patterns."""
        if not self.transaction_data:
            return 0.0
            
        volume = self.transaction_data.get('volume', 0)
        frequency = self.transaction_data.get('frequency', 0)
        
        if volume > 50000 and frequency > 5:
            self.reasons.append("High transaction volume and frequency")
            return 1.0
        return 0 

    def calculate_risk_score(self) -> Tuple[float, Dict[str, float]]:
        """Calculate overall risk score and breakdown."""
        scores = {
            'sanctions_match': self.check_sanctions_match(),
            'pep': self.check_pep_status(),
            'geography': self.assess_geographic_risk(),
            'adverse_media': self.check_adverse_media(),
            'transactions': self.assess_transaction_risk()
        }
        
        weighted_score = sum(
            score * self.RISK_WEIGHTS[factor]
            for factor, score in scores.items()
        )
        
        return weighted_score, scores

    def get_risk_category(self, score: float) -> str:
        """Determine risk category based on score."""
        if score >= 0.7:
            return "High Risk"
        elif score >= 0.4:
            return "Medium Risk"
        return "Low Risk"

    def generate_response(self) -> Dict:
        """Generate final response with risk assessment details."""
        risk_score, breakdown = self.calculate_risk_score()
        entity_id = self.get_entity_id()
        
        # Convert any date fields to strings before returning the response
        for key, value in breakdown.items():
            if isinstance(value, date):
                breakdown[key] = value.isoformat()

        return {
            'entity_id': entity_id,
            'risk_score': round(risk_score, 2),
            'risk_category': self.get_risk_category(risk_score),
            'reasons': self.reasons,
            'breakdown': breakdown
        }
