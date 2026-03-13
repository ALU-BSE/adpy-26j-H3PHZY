import hashlib
import uuid
from django.utils import timezone

class RRAConnector:
    """Mock connector for Rwanda Revenue Authority (RRA) EBM integration."""
    
    @staticmethod
    def sign_receipt(shipment_id, amount):
        """
        Simulates requesting an EBM digital signature for a payment.
        Returns a mock digital signature and receipt number.
        """
        raw_data = f"{shipment_id}-{amount}-{timezone.now().isoformat()}"
        signature = hashlib.sha256(raw_data.encode()).hexdigest()[:16].upper()
        receipt_no = str(uuid.uuid4()).split('-')[0].upper()
        
        return {
            "ebm_signature": signature,
            "receipt_number": f"RRA-{receipt_no}",
            "signed_at": timezone.now().isoformat(),
            "status": "APPROVED"
        }

class RURAConnector:
    """Mock connector for RURA (Transport Authority) verification."""
    
    @staticmethod
    def verify_transport_license(license_no):
        """
        Verifies a driver's transport authorization or vehicle license.
        """
        # Simple mock logic: licenses starting with 'RW-T' are valid
        is_valid = str(license_no).startswith('RW-T')
        
        return {
            "license_no": license_no,
            "is_valid": is_valid,
            "expiry_date": "2027-12-31" if is_valid else None,
            "type": "NATIONAL-COURIER",
            "verified_at": timezone.now().isoformat()
        }

class CustomsService:
    """Service to handle international customs manifest generation."""
    
    @staticmethod
    def generate_manifest_xml(shipment):
        """
        Generates EAC-compliant Customs Manifest XML data.
        """
        # Mock XML structure
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomsManifest>
    <Header>
        <ManifestID>MAN-{uuid.uuid4().hex[:8].upper()}</ManifestID>
        <Exporter>{shipment.sender.username}</Exporter>
        <Origin>RWANDA</Origin>
        <Destination>{shipment.destination.name}</Destination>
    </Header>
    <Payload>
        <TrackingCode>{shipment.tracking_code}</TrackingCode>
        <CargoDescription>{getattr(shipment, 'description', 'General Cargo')}</CargoDescription>
        <ValueRWF>{shipment.tariff * 10}</ValueRWF>
    </Payload>
    <Signature>LOCAL-CUSTOMS-AUTH</Signature>
</CustomsManifest>"""
        return xml_template
