#!/bin/bash
# Backup script for IshemaLink PostgreSQL DB

TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_DIR="/backups"
DB_NAME="ishemalink_db"

mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME..."
docker-compose exec -T db pg_dump -U postgres $DB_NAME > $BACKUP_DIR/backup_$TIMESTAMP.sql

echo "Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.sql"

# Optional: Cleanup backups older than 30 days
find $BACKUP_DIR -type f -name "*.sql" -mtime +30 -delete
