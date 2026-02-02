# Reflection: Domestic vs International Validation in IshemaLink

## Executive Summary

The IshemaLink platform distinguishes between Domestic and International shipment handling based on Rwanda's regulatory framework and operational requirements. This 300-word reflection outlines the architectural decisions and validation strategies that reflect these differences.

---

## Validation Philosophy

### Domestic Shipments
Domestic validation prioritizes **speed and accessibility** for Rwanda's mobile-first courier network. Serving 30 Districts and 416 Sectors requires minimal friction:

- **Phone Validation**: Rwanda standard `+250 7XX XXX XXX` (universal requirement)
- **NID Optional**: Only required for Agent accounts, not for individual customer shipments
- **Documentation**: Minimal metadata (recipient name, phone, weight, description)
- **Status Flow**: Simple 5-state progression (PENDING → IN_TRANSIT → DELIVERED)

**Rationale**: Rural agents operating on basic smartphones over USSD need lightweight, offline-capable data structures. Complex validation delays processing.

### International Shipments
International validation enforces **strict regulatory compliance** for cross-border EAC trade:

- **Mandatory NID/TIN**: Sender TIN + Recipient Passport/TIN for KYC compliance
- **Customs Documentation**: Harmonized System (HS) codes, declared values, origin/destination countries
- **Enhanced Status Tracking**: Includes customs clearance checkpoints
- **Declaration Numbers**: Unique customs reference per shipment

**Rationale**: Kampala, Nairobi, and Goma require declaration compliance. Rwanda Revenue Authority (RRA) enforces TIN verification for all traders.

---

## Technical Implementation

### Code Separation Strategy

```python
# Domestic: Minimal fields
class Shipment(models.Model):
    tracking_number, sender, recipient_name, recipient_phone
    weight_kg, description, status, cost

# International: Compliance fields
class InternationalShipment(models.Model):
    # + sender_tin, recipient_passport, recipient_tin
    # + hs_code, customs_value
    # + CustomsDocument (declaration_number, origin/destination countries)
```

### Validation Differences

| Aspect | Domestic | International |
|--------|----------|-----------------|
| **Phone** | Required (Rwanda standard) | Required + Backup international |
| **NID** | Agent-only | Mandatory for all users |
| **Customs** | None | Mandatory CustomsDocument |
| **Status States** | 6 states | 8 states (includes customs) |
| **Cost Calculation** | Zone-based (Rwanda) | Destination-specific + customs value |

---

## Regulatory Alignment

**Domestic Compliance**:
- Rwanda Civil Aviation and Transport Board regulations
- RURA courier licensing requirements
- Basic KYC for agent registration

**International Compliance**:
- East African Community (EAC) Common External Tariff (CET)
- Rwanda Revenue Authority (RRA) customs declarations
- Magerwa (Rwanda Bonded Warehouses) integration points
- PIMS (Port Information Management System) compatibility

---

## User Experience Impact

**Agents in Kigali (Domestic)**: Register with phone only, start serving customers immediately.

**Traders exporting to Kampala (International)**: Register with TIN/NID, provide HS codes, receive customs reference numbers—overhead is justified by compliance requirement.

---

## Conclusion

The architectural separation isn't arbitrary—it reflects Rwanda's progressive digitization of logistics while maintaining regulatory rigor. Domestic streamlines for speed (mobile-first, offline-capable); International enforces compliance (customs documentation, TIN verification). Together, they position IshemaLink as Rwanda's bridge between local delivery and regional EAC trade.
