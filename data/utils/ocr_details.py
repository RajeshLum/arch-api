import re
import os
import platform

import cv2
import pytesseract
from passporteye import read_mrz

# Configure Tesseract path for Windows
if platform.system() == 'Windows':
    # Update this path to where you installed Tesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# 1
def extract_text_from_passport(image_path):
    """Extract raw text from passport using OCR"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    text = pytesseract.image_to_string(gray)
    return text

# 2 Function to parse raw OCR text
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

# Helper function to parse MRZ date
def _parse_mrz_date(ymd_str):
    """Parse a YYMMDD string from MRZ to YYYY-MM-DD format."""
    if not ymd_str or len(ymd_str) != 6 or not ymd_str.isdigit():
        return None
    yy, mm, dd = int(ymd_str[:2]), int(ymd_str[2:4]), int(ymd_str[4:])
    # Determine the century: If year < 30, assume 2000s, else 1900s (adjust as needed)
    century = 2000 if yy < 30 else 1900
    year = century + yy
    try:
        return f"{year:04d}-{mm:02d}-{dd:02d}"
    except Exception:
        return None

# 3 Function to extract MRZ data
def extract_mrz_data(image_path):
    """Extract MRZ and parse structured data"""
    mrz = read_mrz(image_path)
    if mrz is None:
        return None
    
    mrz_data = mrz.to_dict()
    # Add parsed dates if present
    dob = mrz_data.get("date_of_birth")
    exp = mrz_data.get("expiration_date")
    if dob:
        mrz_data["date_of_birth_parsed"] = _parse_mrz_date(dob)
    if exp:
        mrz_data["expiration_date_parsed"] = _parse_mrz_date(exp)
    return mrz_data

# Function to extract all passport details including MRZ
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