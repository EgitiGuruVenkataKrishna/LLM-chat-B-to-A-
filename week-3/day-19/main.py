import logging
from datetime import datetime,UTC
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# -----------------------------
# DATABASE SETUP
# -----------------------------

DATABASE_URL = "sqlite:///logs.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# -----------------------------
# TABLE MODEL
# -----------------------------

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)
    message = Column(String)
    timestamp = datetime.now(UTC)

# Create tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# LOGGING CONFIGURATION
# -----------------------------

logger = logging.getLogger("sql_logger")
logger.setLevel(logging.INFO)

# -----------------------------
# DATABASE LOGGING FUNCTION
# -----------------------------

def log_to_db(level, message):

    session = SessionLocal()

    log_entry = Log(
        level=level,
        message=message,
        timestamp=datetime.now(UTC)
    )

    session.add(log_entry)
    session.commit()
    session.close()

# -----------------------------
# APPLICATION EXAMPLE
# -----------------------------

def run_application():

    logger.info("Application started")
    log_to_db("INFO", "Application started")

    try:

        x = 10
        y = 0
        result = x / y

        message = f"Division result: {result}"
        logger.info(message)
        log_to_db("INFO", message)

    except Exception as e:

        logger.error(str(e))
        log_to_db("ERROR", str(e))

    finally:

        logger.info("Application finished")
        log_to_db("INFO", "Application finished")

if __name__ == "__main__":
    run_application()