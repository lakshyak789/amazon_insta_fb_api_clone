# Social Clones API

REST API built with Django REST Framework implementing Amazon, Facebook, and Instagram clones.

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Server
```bash
python manage.py runserver
```

### Run Tests with Coverage
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```

## API Endpoints

### Base URL
All endpoints are prefixed with `/v1/`

### Authentication
- `POST /v1/auth/users/` - Register
- `POST /v1/auth/token/login/` - Login
- `POST /v1/auth/token/refresh/` - Refresh token
- `POST /v1/auth/logout/` - Logout
- `GET /v1/auth/me/` - Current user

### Amazon Clone
- `GET/POST /v1/amazon/categories/`
- `GET/POST /v1/amazon/products/`
- `GET /v1/amazon/products/{id}/`
- `GET/POST /v1/amazon/me/cart/`
- `GET/POST /v1/amazon/me/wishlist/`
- `GET/POST /v1/amazon/orders/`
- And 50+ more...

### Facebook Clone
- `GET/POST /v1/facebook/posts/`
- `GET /v1/facebook/posts/feed/`
- `GET/POST /v1/facebook/friends/requests/`
- `GET/POST /v1/facebook/groups/`
- `GET/POST /v1/facebook/pages/`
- And 50+ more...

### Instagram Clone
- `GET/POST /v1/instagram/media/`
- `GET /v1/instagram/feed/`
- `GET/POST /v1/instagram/users/{id}/follow/`
- `GET/POST /v1/instagram/stories/`
- And 50+ more...

## Deployment

See `render.yaml` for Render.com deployment configuration.
