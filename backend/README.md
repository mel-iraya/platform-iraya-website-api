# Backend — run locally

Quick steps to run the Django backend (Windows, cmd.exe).

1. Open cmd and go to project root:

```
cd /d D:\backend
```

2. Activate venv (if `env/` exists):

```
env\Scripts\activate.bat
```

Or create one:

```
python -m venv .venv
.venv\Scripts\activate.bat
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Migrate and (optional) create admin:

```
python manage.py migrate
python manage.py createsuperuser  # optional
```

5. Start server:

```
python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ in your browser.

Troubleshooting:
- ERR_CONNECTION_REFUSED: ensure the dev server is running and listening.
  - Check listening ports:

```
netstat -ano | findstr :8000
```

- Need LAN access: run `python manage.py runserver 0.0.0.0:8000` and (if required) allow port 8000 in Windows Firewall:

```
netsh advfirewall firewall add rule name="Django8000" dir=in action=allow protocol=TCP localport=8000
```

Notes:
- Uses SQLite (`db.sqlite3`) by default.
- Check http://127.0.0.1:8000/admin/blog/post/ for most of the backend functionalities