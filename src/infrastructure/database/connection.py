import logging
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.models import Base


logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


# Ensure database directory exists for SQLite
def ensure_db_directory():
    """Ensure database directory exists for SQLite databases."""
    if "sqlite" in settings.database.url:
        # Extract path from sqlite:///path/to/db.sqlite
        db_path = settings.database.url.replace("sqlite:///", "")
        if not db_path.startswith("/"):
            # Relative path, make it absolute from current working directory
            db_path = Path.cwd() / db_path

        # Create directory if it doesn't exist
        db_dir = Path(db_path).parent
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)

        # Ensure the file can be created by touching it if it doesn't exist
        if not Path(db_path).exists():
            Path(db_path).touch()


# Ensure database directory exists before creating engine
ensure_db_directory()

# Create engine
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database.url
    else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session():
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """Dependency for Flask-SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
