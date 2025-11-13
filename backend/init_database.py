"""
Simple database initialization script
Run this directly: python init_database.py
"""
from app.db.init_db import main
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    main()
