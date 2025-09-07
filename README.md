# ClipThis

ClipThis is a Django web application that brings stream clippers and streamers together. The goal is to make discovering, creating, and sharing great stream highlights effortless for both creators and their communities.

## Overview
- Connects streamers with community clippers
- Central place to submit, curate, and showcase clips
- Built with Django and a SQL database for reliable persistence

## Tech Stack
- Backend: Django (Python)
- Database: SQL (SQLite by default; PostgreSQL/MySQL recommended for production)
- Env/config: `.env` file (not committed)

## Getting Started
Prerequisites:
- Python 3.10+

Setup:
1. Create and activate a virtual environment
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `py -3 -m venv .venv; .\.venv\\Scripts\\Activate.ps1`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with required settings (examples below)
4. Apply migrations: `python manage.py migrate`
5. Run the server: `python manage.py runserver`

## Environment Variables
Create a `.env` file in the project root (kept out of Git). Typical values:
- `SECRET_KEY=your-django-secret-key`
- `DEBUG=true` (use `false` in production)
- `DATABASE_URL=sqlite:///db.sqlite3` (or a Postgres/MySQL URL)

If you already committed `.env` by mistake, remove it from Git history with `git rm --cached .env` and commit the change.

## Database
- Default development database is SQLite (`db.sqlite3`).
- For production, configure `DATABASE_URL` for PostgreSQL or MySQL.

## Contributing
Issues and PRs are welcome. Please keep changes focused and include context in descriptions.
