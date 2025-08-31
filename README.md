# FireFlow - Firewall Management System

FireFlow is a comprehensive firewall management system built with Python and Flask. It provides a clean web interface and API for managing firewalls, filtering policies, and firewall rules.


### Prerequisites

You'll need Python 3.11 or later installed on your system. FireFlow also requires Redis for task processing and can work with SQLite for development.

### Installation

First, clone the repository and navigate to the project directory:

```bash
git clone https://github.com/fireflow/fireflow.git
cd fireflow
```

Install the project using uv (recommended) or pip:

```bash
# Using uv (recommended)
uv sync --all-extras

# Or using pip
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file in the project root with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=12345
FLASK_SECRET_KEY=dev-flask-secret-key-for-development-only-change-in-production

# Database Configuration
DB_URL=sqlite:///data/fireflow.db
DB_ECHO=true

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=dev-jwt-secret-key-for-development-only-change-in-production

# Application Configuration
APP_NAME=FireFlow
APP_VERSION=1.0.0
ENVIRONMENT=development

# Flower Configuration
FLOWER_PORT=5555
FLOWER_BASIC_AUTH=admin:admin

# Logging Configuration
LOG_LEVEL=DEBUG
```

Or just copy .env.example to .env

### Database Setup

Initialize the database with the latest schema:

```bash
# Run database migrations
uv run alembic upgrade head
```

### Starting the Services

We will run FireFlow is using Docker Compose:

```bash
# Quick start - builds and starts all services
make up

# Or using docker-compose directly
docker-compose up --build -d
```

This starts all services:
- **Redis** - Task queue and caching
- **FireFlow App** - Main Flask application  
- **Celery Worker** - Background task processing
- **Flower** - Task monitoring dashboard



### Application URLs

The application will be available at:
- **Main application**: http://localhost:12345
- **API documentation**: http://localhost:12345/apidocs/
- **Health check**: http://localhost:12345/health
- **Flower dashboard**: http://localhost:5555

### Makefile Commands

Available commands:

```bash
make help          # Show all available commands
make test          # Run tests
make migration     # Apply database migrations
make build         # Build Docker images  
make up            # Start all services
make down          # Stop all services
make clean-db      # Clean and recreate database
```

## Using FireFlow

### Web Interface

Access the web interface at http://localhost:12345 to:
- Manage firewalls across different environments
- Create and configure filtering policies
- Define detailed firewall rules
- Monitor system health and task status

### API Usage

Visit Swagger endpoint for ease of use: http://localhost:12345/apidocs/

### Project Structure

FireFlow follows Clean Architecture principles:

```
fireflow/
├── alembic/             # Database migrations
│   └── versions/        # Migration files
├── data/                # SQLite database files
├── src/
│   ├── domain/          # Business logic and entities
│   │   ├── entities/    # Domain entities (Firewall, User, etc.)
│   │   ├── repositories/ # Repository interfaces
│   │   ├── services/    # Domain services
│   │   └── use_cases/   # Application use cases
│   ├── infrastructure/  # External concerns
│   │   ├── auth/        # Authentication services
│   │   ├── celery/      # Async task processing
│   │   ├── config/      # Application configuration
│   │   ├── database/    # Database models and connections
│   │   ├── repositories/ # Repository implementations
│   │   └── web/         # Flask controllers and schemas
│   └── app.py           # Application entry point
├── tests/               # Test suites
│   ├── domain/          # Domain layer tests
│   ├── factories/       # Test data factories
│   └── infrastructure/  # Infrastructure tests
├── .env.example         # Environment variables template
├── alembic.ini          # Alembic configuration
├── docker-compose.yml   # Docker services
├── Dockerfile           # Docker image configuration
├── pyproject.toml       # Python dependencies
└── Makefile             # Build automation
```

