import re
from typing import Tuple


def validate_rwanda_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate Rwanda phone number format: +250 7XX XXX XXX
    
    Args:
        phone: Phone number string
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    pattern = r'^\+2507\d{8}$'
    if re.match(pattern, phone):
        return True, "Valid phone number"
    return False, "Invalid phone format. Must be +250 7XX XXX XXX"


def validate_rwanda_nid(nid: str) -> Tuple[bool, str]:
    """
    Validate Rwanda National ID format: 16 digits starting with 1-9
    
    Args:
        nid: National ID string
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    pattern = r'^[1-9]\d{15}$'
    
    # Check basic format
    if not re.match(pattern, nid):
        return False, "Invalid NID format. Must be 16 numeric digits starting with 1."
    
    # Optional: Add checksum validation if required by Rwanda standards
    # This would require the specific checksum algorithm
    
    return True, "Valid NID"


def validate_phone_quick(phone: str) -> bool:
    """Quick boolean validation for phone"""
    return bool(re.match(r'^\+2507\d{8}$', phone))


def validate_nid_quick(nid: str) -> bool:
    """Quick boolean validation for NID"""
    return bool(re.match(r'^[1-9]\d{15}$', nid))
