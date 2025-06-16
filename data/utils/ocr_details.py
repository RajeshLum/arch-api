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
        'MRZ Data': mrz_data,
        'extract_info': mrz_data
    }

# --- NID Extraction ---
def extract_text_from_nid(image_path):
    """Extract raw text from NID using OCR"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    text = pytesseract.image_to_string(gray)
    return text

from dateutil import parser as date_parser

def parse_nid_text(text):
    """
    Extract key NID/ID details from OCR text for any country. Tries to be robust to various layouts, languages, and label conventions.
    Extracts:
      - NID/ID Number: Any long digit sequence, or after 'ID', 'Identification', etc.
      - Name: After a label (e.g. Name, Nom, Nombre, Holder), or first likely name line.
      - Date of Birth: After a label (DOB, Birth, Naissance), or first date-like string.
      - Father's/Mother's Name: If present.
    """
    data = {}
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # --- ID/NID Number ---
    # Look for digit sequence or label (ID, Card No, etc.)
    id_number = None
    for line in lines:
        # e.g. ID NO: 1234567890123, Card No, Identification No, etc.
        match = re.search(r'(ID(?:ENTIFICATION)?|CARD|NO|NUMBER|NUMERO)[^\d]*(\d{6,})', line, re.IGNORECASE)
        if match:
            id_number = match.group(2)
            break
    if not id_number:
        # fallback: first long digit sequence
        match = re.search(r'(\d{8,})', text)
        if match:
            id_number = match.group(1)
    if id_number:
        data['number'] = id_number

    # --- Date of Birth ---
    dob = None
    for line in lines:
        # Look for a label in any language (DOB, Birth, Naissance, Fecha Nacimiento, etc.)
        if re.search(r'(birth|naissance|nacimiento|dob|geburtsdatum|생년월일|تاريخ الميلاد|дата рождения)', line, re.IGNORECASE):
            match = re.search(r'([0-9]{1,2} [A-Za-z]{3,9} [0-9]{4}|\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})', line)
            if match:
                dob = match.group(1)
                break
    if not dob:
        # fallback: first date-like string in the text
        match = re.search(r'([0-9]{1,2} [A-Za-z]{3,9} [0-9]{4}|\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})', text)
        if match:
            dob = match.group(1)
    if dob:
        data['date_of_birth'] = dob
        # Try to parse date in ISO format
        try:
            # Some OCRs may use dots or slashes, so let dateutil handle it
            dt = date_parser.parse(dob, dayfirst=True, fuzzy=True)
            data['date_of_birth_parsed'] = dt.strftime('%Y-%m-%d')
        except Exception:
            pass

    # --- Name ---
    name = None
    # Try after common labels (Name, Nom, Nombre, Name of Holder, etc.)
    for i, line in enumerate(lines):
        if re.search(r'(name|nom|nombre|nome|नाम|নাম|name of holder)', line, re.IGNORECASE):
            # Try to get the next line if label is alone, else extract after ':'
            after_colon = re.split(r'[:：]', line, 1)
            if len(after_colon) > 1 and after_colon[1].strip():
                candidate = after_colon[1].strip()
                # Accept even if all uppercase (IDs often have uppercase names)
                name = candidate
                break
            elif i+1 < len(lines):
                candidate = lines[i+1]
                if candidate and not candidate.isupper():
                    name = candidate
                    break
    if not name:
        # Look for lines after 'NATIONAL ID CARD' that look like a name
        idx = -1
        for i, line in enumerate(lines):
            if 'NATIONAL ID CARD' in line.upper():
                idx = i
                break
        found_name = False
        if idx != -1:
            # 1. Prioritize all-uppercase (with minor OCR noise), at least two words, mostly alphabetic
            for line in lines[idx+1:idx+6]:
                l = line.strip()
                if (l and len(l.split()) >= 2 and
                    sum(1 for c in l if c.isalpha()) / max(len(l),1) > 0.7 and
                    re.match(r'^[A-Z !.]+$', l) and
                    ':' not in l and '|' not in l):
                    name = l
                    found_name = True
                    break
            # 2. If not found, try previous logic (not all-uppercase, but mostly alphabetic, two+ words)
            if not found_name:
                for line in lines[idx+1:idx+6]:
                    l = line.strip()
                    if (l and len(l.split()) >= 2 and
                        sum(1 for c in l if c.isalpha()) / max(len(l),1) > 0.7 and
                        ':' not in l and '|' not in l):
                        name = l
                        found_name = True
                        break
        # Global fallback if nothing found after NATIONAL ID CARD
        if not found_name:
            for l in lines:
                if (len(l.split()) >= 2 and
                    sum(1 for c in l if c.isalpha()) / max(len(l),1) > 0.7 and
                    ':' not in l and '|' not in l):
                    name = l
                    break
    if not name:
        # Absolute fallback: first line with two+ words and at least 60% alphabetic
        for l in lines:
            if (len(l.split()) >= 2 and
                sum(1 for c in l if c.isalpha()) / max(len(l),1) > 0.6):
                name = l
                break
    if name:
        name_parts = name.split()
        if len(name_parts) >= 2:
            data['first_name'] = name_parts[0]
            data['last_name'] = name_parts[-1]
        else:
            data['first_name'] = name
            data['last_name'] = ''

    # --- Father's Name (optional) ---
    father = None
    for i, line in enumerate(lines):
        if re.search(r"father('|’|’|\s)s? name|père|padre|বাবার|पिता", line, re.IGNORECASE):
            after_colon = re.split(r'[:：]', line, 1)
            if len(after_colon) > 1 and after_colon[1].strip():
                father = after_colon[1].strip()
            elif i+1 < len(lines):
                father = lines[i+1].strip()
            break
    if father:
        data["Father's Name"] = father

    # --- Mother's Name (optional) ---
    mother = None
    for i, line in enumerate(lines):
        if re.search(r"mother('|’|’|\s)s? name|mère|madre|মায়ের|माता", line, re.IGNORECASE):
            after_colon = re.split(r'[:：]', line, 1)
            if len(after_colon) > 1 and after_colon[1].strip():
                mother = after_colon[1].strip()
            elif i+1 < len(lines):
                mother = lines[i+1].strip()
            break
    if mother:
        data["Mother's Name"] = mother

    return data


def extract_nid_info(image_path):
    """Extract all NID details from image"""
    raw_text = extract_text_from_nid(image_path)
    parsed_text = parse_nid_text(raw_text)
    return {
        'Raw OCR Text': raw_text,
        'Parsed Text Data': parsed_text,
        'extract_info': parsed_text
    }


def extract_text_from_driving_license(image_path):
    """Enhanced OCR to extract raw text from a driving license image using pytesseract"""
    # Read image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize image to improve OCR accuracy
    scale_percent = 150  # Upscale by 150%
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LINEAR)

    # Apply adaptive thresholding for better text segmentation
    thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # Optional: Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, h=30)

    # OCR with custom config
    custom_config = r'--oem 3 --psm 6'  # OEM 3 = default engine, PSM 6 = Assume a single uniform block of text
    text = pytesseract.image_to_string(denoised, config=custom_config)

    return text


def parse_driving_license_text(text):
    """
    Extract key driving license details from OCR text. Attempts to extract:
      - License Number
      - Name
      - Date of Birth
      - Issue Date
      - Expiry Date
      - Address (if possible)
    """
    data = {}
    # License Number
    lic_match = re.search(r'(License|DL|Driving Licence|Licence)\s*No\.?\s*[:：]?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
    if lic_match:
        data['license_number'] = lic_match.group(2).strip()
    # Name
    name_match = re.search(r'(Name|Holder)\s*[:：]?\s*([A-Z][a-zA-Z .]+)', text)
    if name_match:
        data['name'] = name_match.group(2).strip()
    # Date of Birth
    dob_match = re.search(r'(DOB|Date of Birth)\s*[:：]?\s*(\d{2}[/-]\d{2}[/-]\d{4})', text, re.IGNORECASE)
    if dob_match:
        data['date_of_birth'] = dob_match.group(2).strip()
    # Issue Date
    issue_match = re.search(r'(Issue Date|Issued On)\s*[:：]?\s*(\d{2}[/-]\d{2}[/-]\d{4})', text, re.IGNORECASE)
    if issue_match:
        data['issue_date'] = issue_match.group(2).strip()
    # Expiry Date
    exp_match = re.search(r'(Expir(y|y Date)|Valid Till|Valid Up To)\s*[:：]?\s*(\d{2}[/-]\d{2}[/-]\d{4})', text, re.IGNORECASE)
    if exp_match:
        data['expiry_date'] = exp_match.group(3).strip()
    # Address (optional, try to grab lines after 'Address')
    addr_match = re.search(r'Address\s*[:：]?\s*(.+)', text, re.IGNORECASE)
    if addr_match:
        data['address'] = addr_match.group(1).strip()
    return data

def extract_driving_license_info(image_path):
    """Extract all Driving License details from image"""
    raw_text = extract_text_from_driving_license(image_path)
    parsed_text = parse_driving_license_text(raw_text)
    
    return {
        'Raw OCR Text': raw_text,
        'Parsed Text Data': parsed_text,
        'extract_info': parsed_text
    }


def extract_text_from_utility_bill(image_path):
    """Extract raw text from a utility bill image using pytesseract"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Optional: preprocess for better OCR
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    text = pytesseract.image_to_string(gray)
    return text


def parse_utility_bill_text(text):
    """Extract key utility bill details from OCR text."""
    import re
    from dateutil import parser as date_parser
    data = {}
    # Bill Number
    bill_no = re.search(r'(Bill\s*No\.?|Account\s*No\.?|Consumer\s*No\.?|Customer\s*ID)\s*[:：]?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
    if bill_no:
        data['bill_number'] = bill_no.group(2).strip()
    # Name
    name = re.search(r'(Name|Customer Name|Account Name)\s*[:：]?\s*([A-Z][a-zA-Z .]+)', text)
    if name:
        data['name'] = name.group(2).strip()
    # Address
    address = re.search(r'(Address|Customer Address)\s*[:：]?\s*(.+)', text)
    if address:
        data['address'] = address.group(2).strip()
    # Billing Date
    billing_date = re.search(r'(Billing Date|Bill Date|Date of Issue)\s*[:：]?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})', text, re.IGNORECASE)
    if billing_date:
        data['billing_date'] = billing_date.group(2).strip()
        try:
            dt = date_parser.parse(billing_date.group(2), dayfirst=True, fuzzy=True)
            data['billing_date_parsed'] = dt.strftime('%Y-%m-%d')
        except Exception:
            pass
    # Due Date
    due_date = re.search(r'(Due Date|Pay By|Payment Due)\s*[:：]?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})', text, re.IGNORECASE)
    if due_date:
        data['due_date'] = due_date.group(2).strip()
        try:
            dt = date_parser.parse(due_date.group(2), dayfirst=True, fuzzy=True)
            data['due_date_parsed'] = dt.strftime('%Y-%m-%d')
        except Exception:
            pass
    # Amount
    amount = re.search(r'(Amount Due|Total Due|Payable Amount|Total Amount)\s*[:：]?\s*([0-9,.]+)', text, re.IGNORECASE)
    if amount:
        data['amount'] = amount.group(2).replace(',', '').strip()
    return data


def extract_utility_bill_info(image_path):
    """Extract all Utility Bill details from image"""
    raw_text = extract_text_from_utility_bill(image_path)
    parsed_text = parse_utility_bill_text(raw_text)
    return {
        'Raw OCR Text': raw_text,
        'Parsed Text Data': parsed_text,
        'extract_info': parsed_text
    }