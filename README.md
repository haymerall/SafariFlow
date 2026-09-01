# SafariFlow

SafariFlow is a multi-tenant SaaS platform for safari and tour operators.

## Current Development Stage

We are currently at the **Project Foundation** stage. The core Django project has been initialized with the necessary folder structure, settings configurations, and scaffolding for the `core`, `accounts`, and `organizations` applications.

Future features such as CRM, inquiries, tours, bookings, and payments are planned but not yet implemented.

## Technology Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Frontend (Planned):** HTML5, CSS3, JavaScript, Bootstrap, Chart.js

## Project Structure

```
SafariFlow/
├── apps/               # Contains modular Django applications
│   ├── core/           # Base models and shared utilities
│   ├── accounts/       # Custom user models and authentication
│   └── organizations/  # Tenant and company boundary logic
├── config/             # Django project configuration
│   ├── settings/       # Split settings (base.py, local.py)
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── docs/               # Project documentation
├── media/              # User-uploaded files
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
└── tests/              # Test suite foundation
```

## Development Setup

1. **Clone the repository.**
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your database credentials and secret key.
   ```bash
   cp .env.example .env
   ```
5. **Database Setup:**
   Ensure PostgreSQL is running and you have created a database matching your `DATABASE_URL`.
6. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
7. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

## Running Tests

To run the test suite:
```bash
python manage.py test
```

## Git Workflow

Follow standard feature branching for future work. Never expose secrets or commit the `.env` file or virtual environment folder.
