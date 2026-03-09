from main import log_to_db, SessionLocal, Log

def test_log_insert():

    log_to_db("INFO", "Test log entry")

    session = SessionLocal()

    log = session.query(Log).filter_by(message="Test log entry").first()

    session.close()

    assert log is not None
    assert log.level == "INFO"