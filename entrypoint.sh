#!/bin/bash

echo $DB_URL

# Apply migrations
python -m alembic upgrade head

# Run the main application
python main.py
