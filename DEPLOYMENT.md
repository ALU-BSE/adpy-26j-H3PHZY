# Deployment Manual: IshemaLink National Rollout

## Target Environment: Clean Ubuntu 22.04 LTS (AOS/KtRN Rwanda Cloud)

### 1. System Preparation
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git
```

### 2. Project Setup
```bash
git clone https://github.com/user/ishemalink.git
cd ishemalink
```

### 3. Environment Configuration
Edit the `.env` file to include **actual production secrets**:
```ini
# !!! REPLACE WITH REAL SECRETS !!!
SECRET_KEY=generate_a_random_64_character_string
DEBUG=False
ALLOWED_HOSTS=api.ishemalink.rw
DB_NAME=ishemalink_db
DB_USER=ishema_admin
DB_PASSWORD=highly_secure_password
DATABASE_URL=postgres://ishema_admin:highly_secure_password@pgbouncer:6432/ishemalink_db
# ... other vars in .env ...
```

### 4. SSL Certificate Generation (Certbot)
Before starting the full stack, generate a staging or production certificate:
```bash
# Start only Nginx for challenge
docker-compose up -d nginx
# Run Certbot (Manual or via script)
docker run --rm -it --name certbot \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot -d api.ishemalink.rw
```

### 5. National Rollout Launch
```bash
# This starts Web, PgBouncer, Postgres, Redis, Celery, and Nginx
docker-compose -f docker-compose.prod.yml up -d --build
```

### 6. Production Verification
- **PgBouncer Check**: `docker-compose exec pgbouncer psql -U pgbouncer -p 6432 -c "SHOW POOLS;"`
- **Health check**: `curl https://api.ishemalink.rw/api/v1/health/deep/`
- **Metrics**: `curl https://api.ishemalink.rw/api/v1/ops/metrics/`

### 7. Post-Launch
- **Seed initial data**: `curl -X POST -H "Authorization: Token <admin_token>" https://api.ishemalink.rw/api/v1/test/seed/`
- **Set up Cron**: Add `scripts/backup_db.sh` to your crontab for automated nightly backups.
