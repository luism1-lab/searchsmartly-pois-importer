SearchSmartly - Take Home Exercise (Production README)

This repository contains my solution for the SearchSmartly takehome exercise.  
The goal is to implement a Django service that imports Points of Interest (PoIs) from CSV, JSON, and XML, and lets you browse them via the Django Admin.

---

Requirements
- Python 3.10+
- pip
- Virtual environment recommended

---

Setup
1. Create and activate a virtual environment
   python -m venv env_ssmtly
   env_ssmtly\Scripts\activate   # Windows

2. Install dependencies
   pip install -r requirements.txt

3. Run migrations
   python manage.py migrate

4. Create a superuser
   python manage.py createsuperuser

5. Import PoI sample data
   python manage.py import_pois sample_data/sample.csv sample_data/sample.json sample_data/sample.xml

6. Start the server
   python manage.py runserver

7. Log into the admin  
   http://127.0.0.1:8000/admin/

---

Admin features
- List PoIs with:
  - Internal ID
  - External ID
  - Name
  - Category
  - Avg. Rating
- Search by internal ID or external ID
- Filter by category

---

Project structure
pois/                      # Django app
  models.py                # PoI model
  admin.py                 # Admin config
  management/commands/     # import_pois command
sample_data/               # Example input files
  sample.csv
  sample.json
  sample.xml
tests/                     # Optional pytest test suite
manage.py
README.md
requirements.txt
pytest.ini
.gitignore

---

Parsing approach
For file parsing, I relied on Python’s standard libraries:
- csv.DictReader for CSV files
- json.load for JSON files
- xml.etree.ElementTree for XML files

These modules are reliable, lightweight, and included in the Python standard library, which avoids external dependencies.  
In a production system with larger or more complex XML files, I would consider lxml for better performance and advanced parsing features.

The logic maps each parsed object to the PoI model and uses update_or_create to ensure idempotency (updates existing records by external_id, creates otherwise).

---

What was done
- Django project created
- PoI model implemented
- Admin configured with search + filter
- Import command for CSV, JSON, XML
- Sample data included

---

Improvements already applied
- Added optional automated tests (pytest + pytest-django)
- Clean repository via .gitignore
- Clear README with setup & usage

---

Future improvements
- Import logs / jobs → model to track which file was imported, counts (created/updated/skipped), and timestamps
- Expose REST API with Django REST Framework
- Normalize categories into a separate model
- User roles & permissions for real estate / business scenarios
- Better validation & error handling for corrupted files (centralized validators)

---

Optional testing
Automated tests included with pytest and pytest-django cover:
- Import from CSV, JSON, XML
- Idempotency checks
- Admin search (internal/external ID) and category filter

Run with:
pytest -q

---

Notes
- Data import is idempotent: if a PoI with the same external_id already exists, it is updated instead of duplicated.
- SQLite is used for simplicity; can be swapped with PostgreSQL/MySQL for production.
