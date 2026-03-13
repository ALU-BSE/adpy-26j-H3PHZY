import re
from typing import Tuple, Dict, Any
from django.core.exceptions import ValidationError

def validate_rwanda_phone(phone: str) -> bool:
    """Quick boolean validation for Rwanda phone"""
    if not phone:
        return False
    clean_phone = phone.replace(" ", "").replace("-", "")
    # Pattern: +250 7 [2,3,8,9] followed by 7 digits
    rwanda_phone_pattern = r'^\+2507[2-9]\d{7}$'
    return bool(re.match(rwanda_phone_pattern, clean_phone))

def validate_rwanda_nid(nid: str) -> bool:
    """Quick boolean validation for Rwanda National ID"""
    if not nid:
        return False
    clean_nid = nid.replace(" ", "").replace("-", "")
    # Pattern: Must be 16 digits, starting with 1
    rwanda_nid_pattern = r'^1\d{15}$'
    return bool(re.match(rwanda_nid_pattern, clean_nid))

def validate_rwanda_phone_detailed(phone: str) -> Tuple[bool, str]:
    """Detailed validation for Rwanda phone with descriptive error messages"""
    if not phone:
        return False, "Phone number is required."
    
    clean_phone = phone.replace(" ", "").replace("-", "")
    
    if not clean_phone.startswith("+250"):
        return False, "Phone number must start with +250 (Rwanda country code)."
    
    if len(clean_phone) != 13:
        return False, f"Phone number must be exactly 13 characters. Got {len(clean_phone)}."
    
    if not clean_phone[4] == '7':
        return False, "Rwanda mobile numbers must start with 7 after country code."
    
    if clean_phone[5] not in ['2', '3', '8', '9']:
        return False, "Invalid operator prefix. Valid prefixes are 72, 73, 78, or 79."
    
    if not clean_phone[4:].isdigit():
        return False, "Phone number must contain only digits after country code."
    
    return True, "Valid phone number"

def validate_rwanda_nid_detailed(nid: str) -> Tuple[bool, str]:
    """Detailed validation for Rwanda NID with descriptive error messages"""
    if not nid:
        return False, "National ID is required."
    
    clean_nid = nid.replace(" ", "").replace("-", "")
    
    if not clean_nid.isdigit():
        return False, "National ID must contain only numeric digits."
    
    if len(clean_nid) != 16:
        return False, f"National ID must be exactly 16 digits. Got {len(clean_nid)}."
    
    if not clean_nid.startswith('1'):
        return False, "Invalid NID format. Must start with 1 (standard post-2008 format)."
    
    return True, "Valid National ID"

def format_rwanda_phone(phone: str) -> str:
    """Format phone number: +250 7XX XXX XXX"""
    clean = re.sub(r'[^\d+]', '', phone)
    if len(clean) == 13 and clean.startswith('+250'):
        return f"{clean[:4]} {clean[4:7]} {clean[7:10]} {clean[10:]}"
    return phone

def format_rwanda_nid(nid: str) -> str:
    """Format NID: XXXX XXXX XXXX XXXX"""
    clean = re.sub(r'\D', '', nid)
    if len(clean) == 16:
        return f"{clean[:4]} {clean[4:8]} {clean[8:12]} {clean[12:]}"
    return nid

# Django-specific validators for Model/Serializer fields
def django_validate_rwanda_phone(value: str) -> None:
    is_valid, error_msg = validate_rwanda_phone_detailed(value)
    if not is_valid:
        raise ValidationError(error_msg)

def django_validate_rwanda_nid(value: str) -> None:
    is_valid, error_msg = validate_rwanda_nid_detailed(value)
    if not is_valid:
        raise ValidationError(error_msg)
