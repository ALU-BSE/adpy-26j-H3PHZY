import re
from typing import Tuple, Optional
from django.conf import settings


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


def validate_rwanda_nid(nid: str, birth_year: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validate Rwanda National ID with several checks:

    - Must be exactly 16 numeric digits.
    - Optional configurable first-digit rule (via `settings.NID_FIRST_DIGIT_ALLOWED`).
      If set to a string of allowed starting digits (e.g. "1" or "12") or an
      iterable of digits, the NID must start with one of those digits.
    - Optional birth year consistency check: if `birth_year` is provided the
      function will attempt to verify the year appears somewhere in the NID
      (this is intentionally generic because NID layouts may vary).

    Args:
        nid: National ID string
        birth_year: optional integer year to verify is consistent with the NID

    Returns:
        Tuple of (is_valid: bool, message: str)
    """

    # Basic numeric and length check
    if not isinstance(nid, str) or not nid.isdigit() or len(nid) != 16:
        return False, "Invalid NID format. Must be exactly 16 numeric digits."

    # First-digit rule (optional)
    allowed_first = getattr(settings, 'NID_FIRST_DIGIT_ALLOWED', None)
    if allowed_first:
        # Normalize allowed_first to an iterable of characters
        if isinstance(allowed_first, str):
            allowed_digits = list(allowed_first)
        else:
            allowed_digits = [str(d) for d in allowed_first]

        if nid[0] not in allowed_digits:
            return False, f"Invalid NID: first digit must be one of {allowed_digits}."

    # Birth-year consistency check (optional)
    if birth_year is not None:
        year_str = str(int(birth_year))
        # Accept either 4-digit year or 2-digit suffix if provided
        if year_str not in nid:
            # also accept 2-digit year if present in NID
            short_year = year_str[-2:]
            if short_year not in nid:
                return False, "Birth year does not appear to match the NID."

    # All checks passed
    return True, "Valid NID"


def validate_phone_quick(phone: str) -> bool:
    """Quick boolean validation for phone"""
    return bool(re.match(r'^\+2507\d{8}$', phone))


def validate_nid_quick(nid: str) -> bool:
    """Quick boolean validation for NID"""
    return bool(re.match(r'^[1-9]\d{15}$', nid))
