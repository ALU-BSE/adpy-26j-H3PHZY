# IshemaLink API

This is the API documentation for the IshemaLink project.

## API Endpoints

- **GET** /api/status/ - System health and database connectivity check
- **GET** /api/ - API root with version information
- **POST** /api/auth/register/ - Register new account.
- **POST** /api/auth/verify-nid/ - Standalone NID check.

## Project Structure

- **core/**: Shared utilities (User, Location)
- **domestic/**: Local delivery logic
- **international/**: Cross-border logic

## Requirements

- Django
- Django REST Framework

## Setup Instructions

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Run migrations using `python manage.py migrate`.
4. Start the server using `python manage.py runserver`.