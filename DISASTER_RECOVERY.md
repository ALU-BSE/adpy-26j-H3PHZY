# Disaster Recovery Plan: IshemaLink National Rollout

## 1. Recovery Point Objective (RPO)
- **Target**: < 15 minutes of data loss.
- **Method**: Automated DB snapshots every 1 hour + WAL (Write-Ahead Logging) archiving.

## 2. Recovery Time Objective (RTO)
- **Target**: < 30 minutes to full service restoration.

## 3. Emergency Scenarios & Procedures

### Scenario A: Total Data Center Outage (e.g., AOS DC failure)
1. **Redirect Traffic**: Update DNS records to secondary region (e.g., KT-RN).
2. **Restore DB**: Pull latest snapshot from S3/MinIO compatible storage.
3. **Re-provision**: Run `docker-compose up -d` on the failover server.

### Scenario B: Massive Database Corruption
1. **Rollback**: Immediately switch to a read-only "Maintenance" mode via `/api/v1/ops/maintenance/toggle/`.
2. **Point-in-Time Recovery**: Use PostgreSQL WAL logs to restore to the state 1 minute prior to corruption.

### Scenario C: Regional Internet Outage (Nyamagabe Outage)
- **Local Persistence**: Mobile clients switch to localized synchronization queue.
- **Manual Reconciliation**: Agents use signed EBM paper receipts which are uploaded via batch OCR once connectivity returns.

## 4. Maintenance Schedule
- **Weekly**: Security patch auditing.
- **Monthly**: Full Disaster Recovery drill (Restore test).
