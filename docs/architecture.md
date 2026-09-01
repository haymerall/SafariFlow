# SafariFlow Architecture

## Overview

SafariFlow is designed as a multi-tenant SaaS platform utilizing Django, Django REST Framework, and PostgreSQL. The system uses a modular app structure to separate concerns and ensure maintainability as the platform grows.

## Implemented Components (Foundation)

- **config:** Holds the Django project settings. Settings are split into modular files (`base.py`, `local.py`, etc.) and rely on environment variables (`django-environ`) for secrets and database connections (`DATABASE_URL`).
- **apps.core:** A foundational app for base models (like UUID abstract models, timestamp abstract models) and common utility functions.
- **apps.accounts:** Contains the custom `User` model inheriting from `AbstractUser`. We start with a custom user model to allow for future role-based or custom field implementations without difficult database migrations later.
- **apps.organizations:** The architectural boundary for multi-tenancy. This app will eventually handle the isolation of company data (Users, Leads, Inquiries, etc.).
- **Testing Foundation:** Dedicated test directory and configuration ready for TDD/BDD.

## Planned Components (Not Yet Implemented)

As per the initial specifications, the following features are planned but intentionally excluded from the initial foundation setup:

- **Multi-Tenancy Logic:** The actual isolation mechanisms (middleware, row-level security, or foreign key filtering) are not yet implemented.
- **CRM & Customers:** Management of customer profiles, leads, and inquiries.
- **Tours & Bookings:** Management of safari packages, itineraries, and booking workflows.
- **Payments & Finance:** Financial tracking, invoicing, and reporting (Finance Officer tools).
- **Operations:** Management of drivers, guides, vehicles, and schedules.
- **Reporting:** Chart.js integration for analytics.

## Architectural Decisions

1. **Custom User Model:** A custom user model (`apps.accounts.User`) was implemented from the start.
2. **Environment Variables:** All sensitive data (database credentials, secret keys) is exclusively loaded via environment variables to ensure security best practices.
3. **Database:** PostgreSQL is selected as the production and development database to support advanced queries and potential future row-level security or json fields, bypassing SQLite completely.
