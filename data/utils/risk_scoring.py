import uuid
from typing import Dict, List, Tuple

from django.db.models import Q

from ..models import SanctionedEntity


class RiskScorer:
    RISK_WEIGHTS = {
        'sanctions_match': 0.40,
        'pep': 0.10,
        'geography': 0.20,
        'adverse_media': 0.20,
        'transactions': 0.10
    }

    COUNTRY_RISK_LEVELS = {
        'HIGH_RISK': [
            'kp',  # Democratic People's Republic of Korea (North Korea)
            'ir',  # Iran
            'mm',  # Myanmar
        ],
        'MEDIUM_RISK': [
            'al',  # Albania
            'bb',  # Barbados
            'bf',  # Burkina Faso
            'bz',  # Belize
            'ci',  # Côte d'Ivoire
            'dm',  # Dominica
            'cd',  # Democratic Republic of the Congo
            'fj',  # Fiji
            'gh',  # Ghana
            'gt',  # Guatemala
            'ht',  # Haiti
            'jm',  # Jamaica
            'jo',  # Jordan
            'lb',  # Lebanon
            'lr',  # Liberia
            'mg',  # Madagascar
            'ml',  # Mali
            'ma',  # Morocco
            'mo',  # Mozambique
            'ne',  # Niger
            'ng',  # Nigeria
            'pa',  # Panama
            'sn',  # Senegal
            'ss',  # South Sudan
            'sr',  # Suriname
            'sy',  # Syria
            'tz',  # Tanzania
            'tt',  # Trinidad and Tobago
            'ug',  # Uganda
            'ae',  # United Arab Emirates
            've',  # Venezuela
            'ye',  # Yemen
        ],
        'LOW_RISK': [
            'us',  # United States
            'gb',  # United Kingdom
            # Add other FATF-compliant countries as needed
        ]
    }

    
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

    # def check_pep_status(self) -> float:
    #     """Check if entity is a PEP."""
    #     # Implement PEP checking logic
    #     # This is a simplified example
    #     pep_match = Person.objects.filter(
    #         political__isnull=False,
    #         name__contains=self.entity_data['name']
    #     ).exists()
        
    #     if pep_match:
    #         self.reasons.append("Entity identified as PEP")
    #         return 1.0
    #     return 0.0

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

    # def check_adverse_media(self) -> float:
    #     """Check for adverse media mentions."""
    #     # Implement adverse media checking logic
    #     # This is a simplified example
    #     has_adverse_media = Person.objects.filter(
    #         name__contains=self.entity_data['name'],
    #         notes__isnull=False
    #     ).exists()
        
    #     if has_adverse_media:
    #         self.reasons.append("Adverse media mentions found")
    #         return 1.0
    #     return 0.0

    def assess_transaction_risk(self) -> float:
        """Assess risk based on transaction patterns."""
        if not self.transaction_data:
            return 0.0
            
        volume = self.transaction_data.get('volume', 0)
        frequency = self.transaction_data.get('frequency', 0)
        
        # Implement transaction risk logic
        if volume > 50000 and frequency > 5:
            self.reasons.append("High transaction volume and frequency")
            return 1.0
        return 0  # Base transaction risk

    def calculate_risk_score(self) -> Tuple[float, Dict[str, float]]:
        """Calculate overall risk score and breakdown."""
        scores = {
            'sanctions_match': self.check_sanctions_match(),
            # 'pep': self.check_pep_status(),
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
        
        return {
            'entity_id': str(uuid.uuid4()),
            'risk_score': round(risk_score, 2),
            'risk_category': self.get_risk_category(risk_score),
            'reasons': self.reasons,
            'breakdown': breakdown
        }
