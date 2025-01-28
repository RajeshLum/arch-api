from typing import Dict, List, Tuple

from django.db.models import Q

from ..models import Organization, Person, SanctionedEntity


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
            'al', 'bb', 'bf', 'bz', 'ci', 'dm', 'cd', 'fj', 'gh', 'gt', 
            'ht', 'jm', 'jo', 'lb', 'lr', 'mg', 'ml', 'ma', 'mo', 'ne', 
            'ng', 'pa', 'sn', 'ss', 'sr', 'sy', 'tz', 'tt', 'ug', 'ae', 
            've', 'ye'
        ],
        'LOW_RISK': ['us', 'gb']
    }

    def __init__(self, entity_id: str, entity_name: str, entity_nationality: str):
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.entity_nationality = entity_nationality
        self.reasons: List[str] = []

    def check_sanctions_match(self, sanctioned_entity: SanctionedEntity) -> Dict:
        """Check sanctions status and return detailed information."""
        datasets = []
        if sanctioned_entity.target:
            if sanctioned_entity.referents and 'OFAC' in str(sanctioned_entity.referents):
                datasets.append('OFAC')
            
            self.reasons.append("Entity found on sanctions list")
            return {
                'status': 'Flagged',
                'datasets': datasets,
                'confidence': 0.95  
            }
        return {
            'status': 'Not Flagged',
            'datasets': [],
            'confidence': 0.0
        } 


    def assess_geographic_risk(self) -> Dict:
        """Assess geographic risk and return detailed information."""
        country = self.entity_nationality.lower()
        
        if country in self.COUNTRY_RISK_LEVELS['HIGH_RISK']:
            return {
                'status': 'High Risk',
                'country': country,
                'reason': 'Listed as high-risk by FATF'
            }
        elif country in self.COUNTRY_RISK_LEVELS['MEDIUM_RISK']:
            return {
                'status': 'Medium Risk',
                'country': country,
                'reason': 'Under increased monitoring by FATF'
            }
        elif country in self.COUNTRY_RISK_LEVELS['LOW_RISK']:
            return {
                'status': 'Low Risk',
                'country': country,
                'reason': 'FATF compliant jurisdiction'
            }
        
        return {
            'status': 'Medium Risk',
            'country': country,
            'reason': 'Country not in FATF assessment list'
        }

    def check_pep_status(self, person: Person) -> Dict:
        """Check PEP status and return detailed information."""
        if person and person.political:
            self.reasons.append("Entity identified as PEP")
            return {'status': 'Flagged'}
        return {'status': 'Not Flagged'}

    def check_adverse_media(self, person: Person) -> Dict:
        """Check adverse media mentions and return detailed information."""
        if person and person.notes:
            self.reasons.append("Adverse media mentions found")
            return {
                'status': 'Flagged',
                'reports': [
                    {
                        'source': 'Internal Notes',
                        'details': note if isinstance(note, str) else str(note)
                    } for note in person.notes[:3]  # Limit to first 3 notes
                ]
            }
        return {'status': 'Not Flagged'}

    def calculate_risk_score(self, sanctioned_entity: SanctionedEntity) -> float:
        """Calculate overall risk score."""
        score = 0.0
        
        # Sanctions check
        sanctions_details = self.check_sanctions_match(sanctioned_entity)
        if sanctions_details['status'] == 'Flagged':
            score += self.RISK_WEIGHTS['sanctions_match']
        
        # Geographic risk
        geo_details = self.assess_geographic_risk()
        if geo_details['status'] == 'High Risk':
            score += self.RISK_WEIGHTS['geography']
        elif geo_details['status'] == 'Medium Risk':
            score += self.RISK_WEIGHTS['geography'] * 0.5
        
        # PEP and adverse media checks for Person
        try:
            person = sanctioned_entity.person
            if self.check_pep_status(person)['status'] == 'Flagged':
                score += self.RISK_WEIGHTS['pep']
            if self.check_adverse_media(person)['status'] == 'Flagged':
                score += self.RISK_WEIGHTS['adverse_media']
        except Person.DoesNotExist:
            pass
        
        return score

    def get_risk_category(self, score: float) -> str:
        """Determine risk category based on score."""
        if score >= 0.7:
            return "High Risk"
        elif score >= 0.4:
            return "Medium Risk"
        return "Low Risk"

    def generate_response(self, sanctioned_entity: SanctionedEntity) -> Dict:
        """Generate final response with risk assessment details."""
        risk_score = self.calculate_risk_score(sanctioned_entity)
        
        try:
            person = sanctioned_entity.person
        except Person.DoesNotExist:
            person = None
        
        return {
            'entity_id': self.entity_id,
            'name': self.entity_name,
            'risk_score': round(risk_score, 2),
            'risk_category': self.get_risk_category(risk_score),
            'details': {
                'sanctions': self.check_sanctions_match(sanctioned_entity),
                'pep': self.check_pep_status(person) if person else {'status': 'Not Applicable'},
                'geography': self.assess_geographic_risk(),
                'adverse_media': self.check_adverse_media(person) if person else {'status': 'Not Applicable'}
            }
        }