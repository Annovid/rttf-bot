#!/bin/bash

# Apply migrations
python -m alembic upgrade head

# Run the main application
python main.py
