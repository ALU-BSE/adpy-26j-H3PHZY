import re

def validate_phone(phone: str) -> bool:
    pattern = r'^\+2507\d{8}$'
    return bool(re.match(pattern, phone))


def validate_nid(nid: str) -> bool:
    pattern = r'^[1-9]\d{15}$'
    return bool(re.match(pattern, nid))
