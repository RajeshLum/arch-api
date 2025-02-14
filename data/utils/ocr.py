from django.db.models import Q
from fuzzywuzzy import fuzz

from data.models import Person


def normalize_name(name):
    """Normalize name by removing special characters and converting to lowercase"""
    if not name:
        return ""
    return "".join(c.lower() for c in name if c.isalnum())

def calculate_person_match_score(person, mrz_data):
    """Calculate match score between Person object and MRZ data"""
    if not mrz_data:
        return 0
    
    score = 0
    max_score = 0
    
    # Helper function to compare fields using fuzzy matching
    def compare_fields(person_field, mrz_field, weight=1):
        if not person_field or not mrz_field:
            return 0, weight
        
        # Handle JSON fields that might contain lists
        if isinstance(person_field, list):
            person_value = person_field[0] if person_field else ""
        else:
            person_value = person_field
            
        return fuzz.ratio(str(person_value).lower(), str(mrz_field).lower()) * weight, weight

    # Compare names
    if person.firstName and person.lastName:
        name_score, weight = compare_fields(
            f"{person.firstName[0]} {person.lastName[0]}" if person.firstName and person.lastName else "",
            f"{mrz_data.get('names', '')} {mrz_data.get('surname', '')}",
            weight=3
        )
        score += name_score
        max_score += 100 * weight

    # Compare passport number
    if person.passportNumber:
        passport_score, weight = compare_fields(
            person.passportNumber[0] if person.passportNumber else "",
            mrz_data.get('number', ''),
            weight=4
        )
        score += passport_score
        max_score += 100 * weight

    # Compare birth date
    if person.birthDate:
        birth_score, weight = compare_fields(
            person.birthDate[0] if person.birthDate else "",
            mrz_data.get('date_of_birth', ''),
            weight=2
        )
        score += birth_score
        max_score += 100 * weight

    # Compare nationality
    if person.nationality:
        nationality_score, weight = compare_fields(
            person.nationality[0] if person.nationality else "",
            mrz_data.get('nationality', ''),
            weight=1
        )
        score += nationality_score
        max_score += 100 * weight

    return (score / max_score * 100) if max_score > 0 else 0

def find_matching_person(mrz_data):
    """Find the most matching Person based on MRZ data"""
    if not mrz_data:
        return None
        
    # Get all persons that might match based on basic criteria
    potential_matches = Person.objects.filter(
        Q(passportNumber__contains=mrz_data.get('number', '')) |
        (Q(firstName__isnull=False) & Q(lastName__isnull=False))
    )

    # Calculate match scores for each potential match
    matches_with_scores = [
        (person, calculate_person_match_score(person, mrz_data))
        for person in potential_matches
    ]
    
    # Sort by score in descending order
    matches_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return the best match if it has a score above threshold
    if matches_with_scores and matches_with_scores[0][1] >= 60:  # 60% threshold
        return matches_with_scores[0][0]
    
    return None