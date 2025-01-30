import re

import cv2
import pytesseract
from passporteye import read_mrz


def extract_text_from_passport(image_path):
    """Extract raw text from passport using OCR"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    text = pytesseract.image_to_string(gray)
    return text

def extract_mrz_data(image_path):
    """Extract MRZ and parse structured data"""
    mrz = read_mrz(image_path)
    if mrz is None:
        return None
    
    mrz_data = mrz.to_dict()
    return mrz_data

def parse_passport_text(text):
    """Extract key passport details from raw OCR text"""
    data = {}

    # Extract Name
    name_match = re.search(r'Given Names(?:\s*):?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
    if name_match:
        data['Given Names'] = name_match.group(1).strip()

    surname_match = re.search(r'Surname(?:\s*):?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
    if surname_match:
        data['Surname'] = surname_match.group(1).strip()

    # Extract Passport Number
    passport_match = re.search(r'Passport\s*No\.?:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
    if passport_match:
        data['Passport Number'] = passport_match.group(1).strip()

    # Extract Nationality
    nationality_match = re.search(r'Nationality(?:\s*):?\s*([A-Za-z]+)', text, re.IGNORECASE)
    if nationality_match:
        data['Nationality'] = nationality_match.group(1).strip()

    # Extract Date of Birth
    dob_match = re.search(r'Date of Birth(?:\s*):?\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if dob_match:
        data['Date of Birth'] = dob_match.group(1).strip()

    # Extract Date of Expiry
    expiry_match = re.search(r'Date of Expiry(?:\s*):?\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if expiry_match:
        data['Date of Expiry'] = expiry_match.group(1).strip()

    return data

def extract_passport_info(image_path):
    """Extract all passport details including MRZ"""
    raw_text = extract_text_from_passport(image_path)
    parsed_text = parse_passport_text(raw_text)
    mrz_data = extract_mrz_data(image_path)

    return {
        'Raw OCR Text': raw_text,
        'Parsed Text Data': parsed_text,
        'MRZ Data': mrz_data
    }

if __name__ == "__main__":
    image_path = "passport_sample.jpg"  # Replace with your image path
    passport_info = extract_passport_info(image_path)

    print("Extracted Passport Information:")
    print(passport_info)
