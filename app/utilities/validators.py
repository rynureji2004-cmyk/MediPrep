import re

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def validate_email(email):
    """Verifies format matches standard RFC regex constraints."""
    if not email:
        return False
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def validate_password_strength(password):
    """Validates password contains at least 8 characters and no spaces."""
    if not password or len(password) < 8 or ' ' in password:
        return False
    return True

def validate_indian_mobile(phone):
    """
    Verifies format matches a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.
    Returns (is_valid, clean_10_digit_string).
    """
    if not phone:
        return True, None
    raw_phone = str(phone).strip()
    clean_phone = raw_phone
    if clean_phone.startswith('+91'):
        clean_phone = clean_phone[3:].strip()
    elif clean_phone.startswith('91') and len(clean_phone) > 10:
        clean_phone = clean_phone[2:].strip()
    elif clean_phone.startswith('0') and len(clean_phone) > 10:
        clean_phone = clean_phone[1:].strip()

    digits = re.sub(r'[\s\-]', '', clean_phone)
    if re.match(r'^[6-9]\d{9}$', digits):
        return True, digits
    return False, raw_phone

def validate_phone(phone):
    """Validates phone number against 10-digit Indian mobile format."""
    is_valid, _ = validate_indian_mobile(phone)
    return is_valid

def validate_date_of_birth(dob_str):
    """
    Validates that a date of birth is a valid date and strictly earlier than today.
    Rejects today's date and all future dates.
    Accepts all dates strictly earlier than today (no adult-age restriction).
    Supports ISO (YYYY-MM-DD), Indian/UK (DD-MM-YYYY, DD/MM/YYYY), and other common formats.
    Returns (is_valid, error_message, normalized_dob_str).
    """
    from datetime import datetime, date
    if not dob_str or not str(dob_str).strip():
        return False, "Date of birth is required.", None

    clean_str = str(dob_str).strip()
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%m-%d-%Y",
    ]

    dob_date = None
    for fmt in formats:
        try:
            dob_date = datetime.strptime(clean_str, fmt).date()
            break
        except ValueError:
            continue

    if dob_date is None:
        return False, "Please enter a valid date of birth.", None

    today = date.today()
    if dob_date >= today:
        return False, "Date of birth must be earlier than today.", None

    return True, None, dob_date.strftime("%Y-%m-%d")


def allowed_file(filename):
    """Checks filename extension against allowed whitelist."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_and_parse_datetime(dt_str):
    """
    Validates that a string contains a valid date and time and parses it.
    Rejects malformed strings or strings missing date or time.
    Supports 12-hour AM/PM format (e.g. '04-11-2026 12:00 PM') and standard formats.
    """
    from datetime import datetime

    if not dt_str or not str(dt_str).strip():
        raise ValueError("Scheduled Date & Time is required. Please select both date and time.")

    clean_str = str(dt_str).strip()

    formats = [
        "%d-%m-%Y %I:%M %p",    # 04-11-2026 12:00 PM
        "%d-%m-%Y %I:%M:%S %p", # 04-11-2026 12:00:00 PM
        "%d/%m/%Y %I:%M %p",    # 04/11/2026 12:00 PM
        "%d/%m/%Y %I:%M:%S %p", # 04/11/2026 12:00:00 PM
        "%Y-%m-%d %I:%M %p",    # 2026-11-04 12:00 PM
        "%Y-%m-%d %I:%M:%S %p", # 2026-11-04 12:00:00 PM
        "%Y-%m-%dT%H:%M",       # ISO format
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",    # SQL format
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%YT%H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
    ]

    parsed_dt = None
    for fmt in formats:
        try:
            parsed_dt = datetime.strptime(clean_str, fmt)
            break
        except ValueError:
            continue

    if parsed_dt is None:
        raise ValueError("Invalid Scheduled Date & Time format. Please select a valid date and time using the picker.")

    if parsed_dt.year < 2000 or parsed_dt.year > 2100:
        raise ValueError("Selected date is out of valid range.")

    return parsed_dt


def format_datetime_display(dt_val):
    """
    Formats a datetime object or string into consistent MediPrep 12-hour AM/PM display format:
    'DD-MM-YYYY hh:mm AM/PM' (e.g. '04-11-2026 12:00 PM').
    """
    if not dt_val:
        return 'Not Scheduled'
    if hasattr(dt_val, 'strftime'):
        return dt_val.strftime('%d-%m-%Y %I:%M %p')
    try:
        dt = validate_and_parse_datetime(dt_val)
        return dt.strftime('%d-%m-%Y %I:%M %p')
    except Exception:
        return str(dt_val)


def is_specialty_matching(doctor_specialty, procedure_category):
    """
    Checks if doctor's registered specialty matches or is compatible with procedure's specialty category.
    Handles multiple slash/comma/ampersand separated specialties (e.g. 'Neurology / Radiology').
    """
    if not doctor_specialty or not str(doctor_specialty).strip():
        return False
    if not procedure_category or not str(procedure_category).strip():
        return False

    doc_tokens = [t.strip().lower() for t in re.split(r'[/,;&]', str(doctor_specialty)) if t.strip()]
    proc_tokens = [t.strip().lower() for t in re.split(r'[/,;&]', str(procedure_category)) if t.strip()]

    for d_tok in doc_tokens:
        for p_tok in proc_tokens:
            if d_tok == p_tok or d_tok in p_tok or p_tok in d_tok:
                return True
    return False



