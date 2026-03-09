# SQL Logging System (Python)

This project demonstrates how to store application logs in a SQL database.

## Features

- SQL database logging
- Structured log storage
- Python + SQLAlchemy integration
- Easy querying of logs

## Setup

1. Install dependencies

pip install -r requirements.txt

2. Run application

python main.py

## Database

The system uses SQLite.

Database file created:
logs.db

## Log Table Schema

id        INTEGER
level     TEXT
message   TEXT
timestamp DATETIME

## Example Query

SELECT * FROM logs;

## Learning Outcome

Understand how to:
- Connect Python with SQL database
- Design log tables
- Store structured logs
- Query logs for debugging