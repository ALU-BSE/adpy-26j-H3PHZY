from django.test import TestCase
from core.validators import validate_rwanda_phone, validate_rwanda_nid, validate_phone_quick, validate_nid_quick


class RwandaPhoneValidationTests(TestCase):
    """Test Rwanda phone number validation"""
    
    def test_valid_phone_numbers(self):
        """Test valid Rwanda phone numbers"""
        valid_phones = [
            "+250788123456",
            "+250799654321",
            "+250700000000",
            "+250789999999",
        ]
        
        for phone in valid_phones:
            is_valid, message = validate_rwanda_phone(phone)
            self.assertTrue(is_valid, f"Expected {phone} to be valid")
            self.assertIn("Valid", message)
    
    def test_invalid_phone_numbers(self):
        """Test invalid Rwanda phone numbers"""
        invalid_phones = [
            "+256788123456",  # Uganda number
            "+250788",  # Too short
            "+25078812345600",  # Too long
            "0788123456",  # Missing + prefix
            "+250677123456",  # Wrong operator (06/08 instead of 07)
            "",  # Empty
            "not-a-phone",  # Invalid format
        ]
        
        for phone in invalid_phones:
            is_valid, message = validate_rwanda_phone(phone)
            self.assertFalse(is_valid, f"Expected {phone} to be invalid")
            self.assertIn("Invalid", message)
    
    def test_phone_quick_validation(self):
        """Test quick phone validation"""
        self.assertTrue(validate_phone_quick("+250788123456"))
        self.assertFalse(validate_phone_quick("+256788123456"))


class RwandaNIDValidationTests(TestCase):
    """Test Rwanda National ID validation"""
    
    def test_valid_nid_numbers(self):
        """Test valid Rwanda NID numbers"""
        valid_nids = [
            "1234567890123456",  # Starts with 1
            "9876543210987654",  # Starts with 9
            "1000000000000000",  # Starting with 1
            "9999999999999999",  # All 9s
        ]
        
        for nid in valid_nids:
            is_valid, message = validate_rwanda_nid(nid)
            self.assertTrue(is_valid, f"Expected {nid} to be valid")
            self.assertIn("Valid", message)
    
    def test_invalid_nid_numbers(self):
        """Test invalid Rwanda NID numbers"""
        invalid_nids = [
            "123456789012345",  # Too short (15 digits)
            "12345678901234567",  # Too long (17 digits)
            "0234567890123456",  # Starts with 0 (invalid)
            "abcd567890123456",  # Contains letters
            "",  # Empty
            "1234567890123  6",  # Contains spaces
        ]
        
        for nid in invalid_nids:
            is_valid, message = validate_rwanda_nid(nid)
            self.assertFalse(is_valid, f"Expected {nid} to be invalid")
            self.assertIn("Invalid", message)
    
    def test_nid_quick_validation(self):
        """Test quick NID validation"""
        self.assertTrue(validate_nid_quick("1234567890123456"))
        self.assertFalse(validate_nid_quick("0234567890123456"))
        self.assertFalse(validate_nid_quick("123456789012345"))  # Too short
