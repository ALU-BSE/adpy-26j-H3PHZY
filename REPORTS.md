# IshemaLink National Rollout Technical Reports

## 1. Integration Report: Domestic vs. International Logic
### The Challenge
Initially, IshemaLink had fragmented logic for domestic shipments (using local districts/sectors) and international cargo (using TINs/Passports). This created friction in the "Grand Integration" phase, where a single driver might handle a domestic feeder leg for an international shipment.

### The Solution: The Unified Booking Engine
We implemented a `BookingService` layer that abstracts the commonalities of both modules. 
- **Polymorphism**: The core `Shipment` model handles global tracking and financial state, while specialized app-level models handle the metadata (Customs XML vs. Sector routes).
- **Atomic Orchestration**: By using `transaction.atomic()`, we ensured that a shipment is never partially created. If the RRA EBM signature request fails, the entire booking is rolled back, preventing revenue leakage.

---

## 2. Scalability Plan: 50,000 Users Strategy
To scale from 5,000 to 50,000 users, IshemaLink will adopt a "Shared-Nothing" architecture:

### Phase A: Database Scaling
- **Read Replicas**: Deploy read-only PostgreSQL nodes in different regions (e.g., Kigali and Rubavu) to offload GET requests.
- **Horizontal Sharding**: Partition shipments by year or district to prevent index bloat.

### Phase B: Compute Scaling
- **Kubernetes (K8s) Orchestration**: Transition Docker Compose to K8s for auto-scaling web pods based on CPU/Memory saturation.
- **CDN Offloading**: Serve all static manifests and customs images via a local CDN (e.g., KtRN edge nodes).

---

## 3. Local Context Essay: Why IshemaLink Succeeds in Rwanda
### The "Generic Software" Failure
Most generic logistics software (e.g., DHL clones) fails in Rwanda because they assume high-speed internet in all sectors and don't account for the unique NID/Phone validation patterns of Rwandans. Generic systems often reject "Sector-level" addresses as "incomplete," causing invalid courier routing.

### The IshemaLink Advantage
1. **Operator-Aware Validation**: Our system understands the difference between MTN and Airtel prefixes, ensuring SMS notifications actually reach the rural "Harvest Peak" agents.
2. **Offline Resilience**: Our mobile sync logic handles the 4-hour internet outages common in hilly terrains like Nyamagabe by using localized SQLite buffers that sync when 3G/4G returns.
3. **GovTech Native**: By integrating directly with RRA and RURA at the API level, we eliminate the 3-day delay usually caused by manual tax document reconciliation. IshemaLink isn't just a tracking tool; it's a digital bridge to Rwandan government infrastructure.
