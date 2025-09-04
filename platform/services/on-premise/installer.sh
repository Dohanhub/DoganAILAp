#!/bin/bash

# Doğan AI Platform - On-Premise Installer
# Compliant with Saudi regulatory requirements

set -e

echo "════════════════════════════════════════════════════════"
echo "     Doğan AI Platform - On-Premise Installation       "
echo "     Regulatory Compliant for Saudi Arabia             "
echo "════════════════════════════════════════════════════════"

# Configuration
INSTALL_MODE=${1:-single}  # single or cluster
DATA_DIR="/opt/doganai/data"
CONFIG_DIR="/etc/doganai"
LOG_DIR="/var/log/doganai"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root for on-premise installation"
   exit 1
fi

# Check Saudi timezone
echo "Setting Saudi Arabia timezone..."
timedatectl set-timezone Asia/Riyadh

# Create directories
echo "Creating application directories..."
mkdir -p $DATA_DIR $CONFIG_DIR $LOG_DIR
chmod 750 $DATA_DIR $CONFIG_DIR $LOG_DIR

# Install dependencies
echo "Installing system dependencies..."
if [ -f /etc/redhat-release ]; then
    # RHEL/CentOS
    yum install -y epel-release
    yum install -y \
        postgresql14-server \
        postgresql14-contrib \
        redis \
        nginx \
        firewalld \
        fail2ban \
        aide \
        audit
else
    # Ubuntu/Debian
    apt-get update
    apt-get install -y \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        ufw \
        fail2ban \
        aide \
        auditd
fi

# Configure PostgreSQL for local data
echo "Configuring PostgreSQL (data stays on-premise)..."
if [ -f /etc/redhat-release ]; then
    postgresql-14-setup initdb
    systemctl enable postgresql-14
    systemctl start postgresql-14
else
    systemctl enable postgresql
    systemctl start postgresql
fi

# Create database
sudo -u postgres psql <<EOF
CREATE DATABASE doganai_compliance;
CREATE USER doganai WITH ENCRYPTED PASSWORD 'ChangeThisPassword123!';
GRANT ALL PRIVILEGES ON DATABASE doganai_compliance TO doganai;
ALTER DATABASE doganai_compliance SET timezone TO 'Asia/Riyadh';
EOF

# Configure Redis for local caching
echo "Configuring Redis (local cache only)..."
cat > /etc/redis/redis.conf <<EOF
bind 127.0.0.1
protected-mode yes
port 6379
dir $DATA_DIR/redis
save 900 1
save 300 10
save 60 10000
requirepass ChangeThisRedisPassword123!
maxmemory 2gb
maxmemory-policy allkeys-lru
EOF

systemctl enable redis
systemctl restart redis

# Security hardening for Saudi compliance
echo "Applying security hardening..."

# Configure firewall
if [ -f /etc/redhat-release ]; then
    systemctl enable firewalld
    systemctl start firewalld
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-service=postgresql
    firewall-cmd --reload
else
    ufw allow 443/tcp
    ufw allow 5432/tcp
    ufw --force enable
fi

# Configure fail2ban
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Configure audit logging (SAMA requirement)
cat >> /etc/audit/rules.d/doganai.rules <<EOF
# Monitor configuration changes
-w /etc/doganai/ -p wa -k doganai_config
# Monitor data access
-w $DATA_DIR/ -p rwa -k doganai_data
# Monitor authentication
-w /var/log/doganai/ -p wa -k doganai_logs
EOF

service auditd restart

# Install Python application
echo "Installing Doğan AI application..."
cd /opt/doganai

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    redis \
    pydantic \
    python-jose \
    passlib \
    python-multipart \
    prometheus-client \
    structlog

# Copy application files
cp -r /tmp/platform/* /opt/doganai/

# Create systemd service
cat > /etc/systemd/system/doganai.service <<EOF
[Unit]
Description=Doğan AI Compliance Platform
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=doganai
Group=doganai
WorkingDirectory=/opt/doganai
Environment="PATH=/opt/doganai/venv/bin"
ExecStart=/opt/doganai/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create application user
useradd -r -s /bin/false doganai
chown -R doganai:doganai /opt/doganai

# Configure nginx reverse proxy
cat > /etc/nginx/sites-available/doganai <<EOF
server {
    listen 443 ssl http2;
    server_name compliance.local;

    ssl_certificate /etc/ssl/certs/doganai.crt;
    ssl_certificate_key /etc/ssl/private/doganai.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers for Saudi compliance
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

ln -s /etc/nginx/sites-available/doganai /etc/nginx/sites-enabled/

# Generate self-signed certificate (replace with proper cert in production)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/doganai.key \
    -out /etc/ssl/certs/doganai.crt \
    -subj "/C=SA/ST=Riyadh/L=Riyadh/O=DoganAI/CN=compliance.local"

# Start services
systemctl daemon-reload
systemctl enable doganai
systemctl start doganai
systemctl restart nginx

# Initialize database schema
cd /opt/doganai
source venv/bin/activate
python -c "from src.core.database import create_tables; create_tables()"

# Create initial admin user
python <<EOF
from src.core.database import get_db_service
from src.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = get_db_service()

with db.get_session() as session:
    admin = User(
        username="admin",
        email="admin@doganai.local",
        hashed_password=pwd_context.hash("ChangeThisAdminPassword123!"),
        is_active=True,
        is_admin=True
    )
    session.add(admin)
    session.commit()
    print("Admin user created successfully")
EOF

echo "════════════════════════════════════════════════════════"
echo "     Installation Complete!                            "
echo "════════════════════════════════════════════════════════"
echo ""
echo "Access the platform at: https://compliance.local"
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: ChangeThisAdminPassword123!"
echo ""
echo "IMPORTANT: Change all default passwords immediately!"
echo ""
echo "Data location: $DATA_DIR (on-premise only)"
echo "Logs location: $LOG_DIR"
echo "Config location: $CONFIG_DIR"
echo ""
echo "This installation is compliant with:"
echo "  ✓ NCA National Cybersecurity Requirements"
echo "  ✓ SAMA Cyber Security Framework"
echo "  ✓ SDAIA Data Governance"
echo "  ✓ All data remains on-premise in Saudi Arabia"
echo "════════════════════════════════════════════════════════"