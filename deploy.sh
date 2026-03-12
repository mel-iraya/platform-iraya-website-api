#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Automated Ubuntu VPS Deployment for platform-iraya-website-api
# =============================================================================
# Usage:
#   1. Clone the repo onto your Ubuntu VPS
#   2. cd platform-iraya-website-api
#   3. sudo bash deploy.sh
#
# This script will:
#   • Install system packages (Python 3, PostgreSQL 16, Nginx)
#   • Create a local PostgreSQL database & user
#   • Set up a Python virtual environment and install dependencies
#   • Generate the .env file
#   • Run Django migrations & restore your database dump
#   • Collect static files
#   • Configure Gunicorn as a systemd service
#   • Configure Nginx as a reverse proxy
#   • Prompt you to create a Django superuser
# =============================================================================

set -euo pipefail

# ── Colors for output ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Pre-flight checks ───────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (use: sudo bash deploy.sh)"
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
WSGI_MODULE="blog_project.wsgi:application"
SERVICE_NAME="iraya-api"
NGINX_SITE="iraya-api"
DB_NAME="iraya_web_db"
DB_USER="iraya_admin"
DUMP_FILE="$PROJECT_DIR/iraya_web_db_backup.dump"

info "Project directory: $PROJECT_DIR"

# ── 1. Prompt for server info ────────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Server Configuration${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

read -rp "Enter your VPS public IP or domain name: " SERVER_HOST
if [[ -z "$SERVER_HOST" ]]; then
    error "Server IP/domain cannot be empty."
fi

read -rp "Enter a PostgreSQL password for user '$DB_USER' (leave blank to auto-generate): " DB_PASSWORD
if [[ -z "$DB_PASSWORD" ]]; then
    DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
    info "Auto-generated DB password: $DB_PASSWORD"
fi

DJANGO_SECRET_KEY=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(50)))
" 2>/dev/null || openssl rand -base64 50 | head -c 50)

echo ""
info "Server host:  $SERVER_HOST"
info "DB name:      $DB_NAME"
info "DB user:      $DB_USER"
echo ""

# ── 2. System packages ──────────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 1/8 — Installing System Packages${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

apt-get update -y
apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    libpq-dev gcc \
    curl gnupg2 lsb-release

success "Base system packages installed."

# ── 3. Install PostgreSQL 16 ────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 2/8 — Installing PostgreSQL${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

if ! command -v psql &>/dev/null; then
    # Add the official PostgreSQL APT repository
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list'
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
    apt-get update -y
    apt-get install -y postgresql-18
    success "PostgreSQL 18 installed."
else
    warn "PostgreSQL is already installed ($(psql --version))."
fi

systemctl enable postgresql
systemctl start postgresql
success "PostgreSQL service is running."

# ── 4. Configure PostgreSQL database & user ──────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 3/8 — Configuring PostgreSQL Database${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

# Create user if it doesn't exist
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Update the password in case the user already existed
sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Create database if it doesn't exist
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Grant schema permissions (PostgreSQL 15+ requires this)
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

success "Database '$DB_NAME' and user '$DB_USER' configured."

# ── 5. Python virtual environment & dependencies ────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 4/8 — Setting Up Python Virtual Environment${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

success "Virtual environment created and dependencies installed."

# ── 6. Generate .env file ────────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 5/8 — Generating .env File${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

ENV_FILE="$PROJECT_DIR/.env"

cat > "$ENV_FILE" <<EOF
# Django
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$SERVER_HOST,localhost,127.0.0.1

# PostgreSQL Database (local)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
EOF

chmod 600 "$ENV_FILE"
success ".env file generated at $ENV_FILE"

# ── 7. Django migrations & data restore ──────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 6/8 — Running Migrations & Restoring Data${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_DIR"

# Run migrations to create the schema
python manage.py migrate --noinput
success "Django migrations applied."

# Restore from dump if the dump file exists
if [[ -f "$DUMP_FILE" ]]; then
    info "Restoring database from $DUMP_FILE ..."

    # pg_restore into the local DB. Use --no-owner so objects are owned by DB_USER.
    # --clean drops existing objects first to avoid conflicts with migrate.
    # --if-exists avoids errors when objects don't exist yet.
    PGPASSWORD="$DB_PASSWORD" pg_restore \
        --host=localhost \
        --port=5432 \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --no-owner \
        --clean \
        --if-exists \
        "$DUMP_FILE" || warn "pg_restore completed with warnings (some are normal for a clean restore)."

    success "Database restored from dump."
else
    warn "No dump file found at $DUMP_FILE — skipping data restore."
    warn "The database has empty tables from migrations only."
fi

# Collect static files
python manage.py collectstatic --noinput
success "Static files collected."

# ── Fix file permissions for Nginx ───────────────────────────────────────────
info "Setting file permissions for Nginx (www-data) ..."

# Nginx (www-data) needs execute (traversal) permission on EVERY parent
# directory in the path leading to the project. Without this, Nginx gets
# 403 Forbidden even if the files themselves are readable.
CURRENT_DIR="$PROJECT_DIR"
while [[ "$CURRENT_DIR" != "/" ]]; do
    chmod o+x "$CURRENT_DIR"
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

# Make static and media files world-readable
chmod -R 755 "$PROJECT_DIR/staticfiles"
chmod -R 755 "$PROJECT_DIR/media"

success "File permissions set — Nginx can now serve static and media files."

# ── 8. Gunicorn systemd service ──────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 7/8 — Configuring Gunicorn Service${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

GUNICORN_BIN="$VENV_DIR/bin/gunicorn"

cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Iraya API Gunicorn Daemon
After=network.target postgresql.service

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$GUNICORN_BIN \\
    --workers 3 \\
    --bind 127.0.0.1:8000 \\
    --access-logfile /var/log/iraya-api-access.log \\
    --error-logfile /var/log/iraya-api-error.log \\
    $WSGI_MODULE
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# Give gunicorn a moment to start, then check
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    success "Gunicorn service '$SERVICE_NAME' is running."
else
    warn "Gunicorn service may not have started correctly. Check: journalctl -u $SERVICE_NAME"
fi

# ── 9. Nginx reverse proxy ──────────────────────────────────────────────────
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 8/8 — Configuring Nginx${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

apt-get install -y nginx

cat > "/etc/nginx/sites-available/${NGINX_SITE}" <<EOF
server {
    listen 80;
    server_name $SERVER_HOST;

    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (uploaded images, PDFs, etc.)
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy everything else to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF

# Enable the site
ln -sf "/etc/nginx/sites-available/${NGINX_SITE}" "/etc/nginx/sites-enabled/"

# Remove the default site if it exists
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t || error "Nginx configuration test failed!"
systemctl enable nginx
systemctl restart nginx

success "Nginx configured and running."

# ── 10. Django superuser ─────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Create Django Superuser${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

read -rp "Would you like to create a Django superuser now? (y/N): " CREATE_SUPER
if [[ "$CREATE_SUPER" =~ ^[Yy]$ ]]; then
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    python manage.py createsuperuser
fi

# ── Done! ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅  Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  API:    ${CYAN}http://$SERVER_HOST/api/${NC}"
echo -e "  Admin:  ${CYAN}http://$SERVER_HOST/admin/${NC}"
echo -e "  Media:  ${CYAN}http://$SERVER_HOST/media/${NC}"
echo ""
echo -e "  Gunicorn service: ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
echo -e "  Nginx service:    ${YELLOW}sudo systemctl status nginx${NC}"
echo -e "  Gunicorn logs:    ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Access log:       ${YELLOW}/var/log/iraya-api-access.log${NC}"
echo -e "  Error log:        ${YELLOW}/var/log/iraya-api-error.log${NC}"
echo ""
echo -e "  ${YELLOW}Remember to configure your firewall:${NC}"
echo -e "    sudo ufw allow 80/tcp"
echo -e "    sudo ufw allow 443/tcp"
echo -e "    sudo ufw allow OpenSSH"
echo -e "    sudo ufw enable"
echo ""
