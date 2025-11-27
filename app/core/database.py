# app/core/database.py
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up logging
log = logging.getLogger(__name__)

# Load .env file if it exists
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    # Try loading from current directory as fallback
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file. Example: "
        "DATABASE_URL=postgresql://user:password@localhost:5432/invoice_cc_db"
    )

# Create engine with connection pooling and better error handling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,  # 10 second connection timeout
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        error_msg = str(e)
        log.error(f"Database connection error: {error_msg}")
        
        # Provide helpful error message based on the error
        if "Connection refused" in error_msg or "could not connect" in error_msg.lower():
            raise ConnectionError(
                "Cannot connect to PostgreSQL database. "
                "Please ensure PostgreSQL is running:\n"
                "  - If using Docker: run 'docker-compose up -d postgres'\n"
                "  - If using local PostgreSQL: ensure the service is running\n"
                "  - Check that DATABASE_URL in .env is correct\n"
                f"  - Attempted connection: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'N/A'}"
            )
        else:
            raise ConnectionError(
                f"Database connection failed: {error_msg}\n"
                "Please check your DATABASE_URL configuration in .env"
            )
    except Exception as e:
        log.error(f"Unexpected database error: {str(e)}")
        raise
    finally:
        db.close()
