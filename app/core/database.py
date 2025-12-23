from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Tạo engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Tạo SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


# Dependency để lấy database session
def get_db():
    """
    Database session dependency với transaction management.
    - Tự động commit khi request thành công
    - Tự động rollback khi có exception
    - Luôn đóng connection trong finally block
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit nếu không có exception
    except Exception:
        db.rollback()  # Rollback nếu có exception
        raise
    finally:
        db.close()  # Luôn đóng connection

