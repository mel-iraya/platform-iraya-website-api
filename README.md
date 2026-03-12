# platform-iraya-website-api

Django REST API backend for the Iraya platform website.

## Tech Stack

- **Django 6** + Django REST Framework
- **PostgreSQL 18**
- **Gunicorn** (WSGI server)
- **Nginx** (reverse proxy)

---

## Local Development (Windows)

1. **Create and activate a virtual environment:**

   ```
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

2. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

3. **Set up your `.env`** (copy from `.env.example` or create manually):

   ```
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=iraya_web_db
   DB_USER=iraya_admin
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Run migrations and start the server:**

   ```
   python manage.py migrate
   python manage.py createsuperuser   # optional
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/api/ in your browser.

---

## Production Deployment (Ubuntu VPS)

A fully automated deployment script is included. It installs and configures everything on a fresh Ubuntu server.

### Prerequisites

- A fresh Ubuntu VPS (22.04 or later) with root/sudo access
- The repo cloned onto the server
- The `iraya_web_db_backup.dump` file in the project root (included in the repo)

### Steps

1. **SSH into your VPS:**

   ```bash
   ssh root@your-vps-ip
   ```

2. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd platform-iraya-website-api
   ```

3. **Run the deployment script:**

   ```bash
   sudo bash deploy.sh
   ```

4. **Follow the prompts** — the script will ask for:
   - Your VPS public IP or domain name
   - A PostgreSQL password (or auto-generates one)
   - Django superuser credentials (at the end)

### What the script does

| Step | Action                                                          |
|------|-----------------------------------------------------------------|
| 1    | Installs Python 3, pip, venv, and build dependencies            |
| 2    | Installs PostgreSQL 18 from the official APT repository         |
| 3    | Creates the database and database user with proper permissions  |
| 4    | Creates a Python virtual environment and installs dependencies  |
| 5    | Generates a production `.env` (DEBUG=False, new secret key)     |
| 6    | Runs Django migrations and restores data from the `.dump` file  |
| 7    | Collects static files and sets Nginx file permissions           |
| 8    | Creates a Gunicorn systemd service (`iraya-api.service`)        |
| 9    | Configures Nginx as a reverse proxy with static/media serving   |

### After deployment

| URL                         | Description          |
|-----------------------------|----------------------|
| `http://<IP>/api/`          | DRF Browsable API    |
| `http://<IP>/admin/`        | Django Admin Panel   |
| `http://<IP>/media/`        | Uploaded media files |

### Useful commands

```bash
sudo systemctl status iraya-api      # Check Gunicorn
sudo systemctl restart iraya-api     # Restart Gunicorn
sudo systemctl status nginx          # Check Nginx
sudo journalctl -u iraya-api -f      # Live Gunicorn logs
```

### Firewall setup

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow OpenSSH
sudo ufw enable
```