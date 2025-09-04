# SkillForge AI - User Service

A comprehensive FastAPI-based user management service for the SkillForge AI platform, providing authentication, user profiles, and company management functionality.

## Features

### Authentication & Security
- JWT-based authentication with access and refresh tokens
- Role-based access control (User, Premium User, Moderator, Admin)
- Email verification and password reset functionality
- Session management with device tracking
- Rate limiting and security headers
- Password strength validation

### User Management
- User registration and profile management
- Skills and interests tracking
- User settings and preferences
- Public and private profile visibility
- Account deactivation and deletion

### Company Management
- Company profile creation and management
- Team member invitation and management
- Role-based permissions within companies
- Company verification system
- Public company directory

### Technical Features
- Async/await throughout for high performance
- PostgreSQL database with SQLModel/SQLAlchemy
- Database migrations with Alembic
- Comprehensive input validation with Pydantic
- Full test coverage with pytest
- Email service integration
- Monitoring and logging

## Project Structure

```
user-service/
├── app/
│   ├── models/          # SQLModel database models
│   │   ├── user.py      # User, UserSettings, UserSession models
│   │   ├── company.py   # Company and team management models
│   │   └── base.py      # Base model mixins
│   ├── schemas/         # Pydantic request/response schemas
│   │   ├── user.py      # User-related schemas
│   │   └── company.py   # Company-related schemas
│   ├── crud/            # Database operations
│   │   ├── user.py      # User CRUD operations
│   │   ├── company.py   # Company CRUD operations
│   │   └── base.py      # Base CRUD class
│   ├── api/             # FastAPI route handlers
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py      # Authentication endpoints
│   │           ├── users.py     # User management endpoints
│   │           └── companies.py # Company management endpoints
│   ├── core/            # Core functionality
│   │   ├── config.py    # Configuration and settings
│   │   ├── database.py  # Database setup and session management
│   │   └── security.py  # Authentication and security utilities
│   ├── utils/           # Utility functions
│   │   ├── email.py     # Email sending functionality
│   │   ├── validators.py # Input validation utilities
│   │   └── helpers.py   # General helper functions
│   └── tests/           # Test suite
│       ├── conftest.py  # Test configuration and fixtures
│       ├── test_auth.py # Authentication tests
│       ├── test_users.py # User management tests
│       └── test_companies.py # Company management tests
├── alembic/             # Database migrations
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── alembic.ini         # Alembic configuration
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

1. **Clone the repository and navigate to user-service:**
   ```bash
   cd apps/backend/user-service
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and other settings
   ```

5. **Set up database:**
   ```bash
   # Create database
   createdb skillforge_users

   # Run migrations
   alembic upgrade head
   ```

6. **Run the application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **API Documentation:** http://localhost:8000/api/v1/docs
- **Alternative Docs:** http://localhost:8000/api/v1/redoc
- **Health Check:** http://localhost:8000/health

## Configuration

Key environment variables:

```bash
# Environment
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/skillforge_users

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@skillforge-ai.com

# First superuser (optional)
FIRST_SUPERUSER=admin@skillforge-ai.com
FIRST_SUPERUSER_PASSWORD=changethis123
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout current session
- `POST /api/v1/auth/logout-all` - Logout all sessions
- `POST /api/v1/auth/verify-email-request` - Request email verification
- `POST /api/v1/auth/verify-email` - Verify email with token
- `POST /api/v1/auth/password-reset-request` - Request password reset
- `POST /api/v1/auth/password-reset-confirm` - Reset password with token

### User Management
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `POST /api/v1/users/me/change-password` - Change password
- `GET /api/v1/users/me/settings` - Get user settings
- `PUT /api/v1/users/me/settings` - Update user settings
- `DELETE /api/v1/users/me` - Delete current user account

### Public User Profiles
- `GET /api/v1/users/public` - Get public user profiles (with search)
- `GET /api/v1/users/{user_id}/public` - Get specific public user profile

### Admin User Management
- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (admin only)
- `PUT /api/v1/users/{user_id}/role` - Update user role (admin only)
- `PUT /api/v1/users/{user_id}/status` - Update user status (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Company Management
- `POST /api/v1/companies/` - Create company profile
- `GET /api/v1/companies/my-companies` - Get user's companies
- `GET /api/v1/companies/{company_id}` - Get company details
- `PUT /api/v1/companies/{company_id}` - Update company profile
- `DELETE /api/v1/companies/{company_id}` - Delete company

### Public Company Profiles
- `GET /api/v1/companies/public/search` - Search public company profiles
- `GET /api/v1/companies/public/{company_id}` - Get public company profile
- `GET /api/v1/companies/slug/{slug}` - Get company by slug

### Team Management
- `GET /api/v1/companies/{company_id}/members` - Get team members
- `POST /api/v1/companies/{company_id}/members` - Invite team member
- `PUT /api/v1/companies/{company_id}/members/{member_id}` - Update team member
- `DELETE /api/v1/companies/{company_id}/members/{member_id}` - Remove team member

## Database Schema

### Key Models

**User Model:**
- Authentication fields (email, username, hashed_password)
- Profile information (name, bio, avatar, location)
- Professional details (job_title, experience_level, skills)
- Account management (role, status, verification)
- Settings and preferences

**Company Model:**
- Basic information (name, description, logo, website)
- Contact and location details
- Business information (industry, size, founded_year)
- Social media links
- Subscription and billing details

**Team Membership Model:**
- User-company relationships
- Role-based permissions
- Invitation and acceptance tracking

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py

# Run with verbose output
pytest -v
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history
```

## Development

### Code Style
- Follow PEP 8 style guidelines
- Use type hints throughout
- Add docstrings to all functions and classes
- Format code with Black: `black app/`
- Sort imports with isort: `isort app/`

### Adding New Features
1. Create/update models in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Implement CRUD operations in `app/crud/`
4. Create API endpoints in `app/api/v1/endpoints/`
5. Add comprehensive tests in `app/tests/`
6. Update documentation

## Deployment

### Docker
```bash
# Build image
docker build -t skillforge-ai-user-service .

# Run container
docker run -p 8000:8000 --env-file .env skillforge-ai-user-service
```

### Production Considerations
- Use environment variables for all sensitive configuration
- Set up proper logging and monitoring
- Configure rate limiting and security headers
- Use HTTPS in production
- Set up database backups
- Configure email service (SMTP)
- Set up Redis for session caching (optional)

## License

Part of the SkillForge AI platform - All rights reserved.

## Support

For support and questions, please contact the development team or create an issue in the project repository.