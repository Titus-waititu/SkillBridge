"""Search for specific job titles in the database"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys
sys.path.append("app")


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

search_terms = [
    "developer",
    "engineer",
    "programmer",
    "software",
    "frontend",
    "backend",
    "full stack",
    "data scientist",
    "machine learning"
]

with engine.connect() as conn:
    for term in search_terms:
        result = conn.execute(text(f"""
            SELECT title, company, location, experience_level
            FROM job_postings
            WHERE LOWER(title) LIKE LOWER('%{term}%')
            LIMIT 3
        """))

        rows = result.fetchall()
        if rows:
            print(f"\n🔍 Jobs matching '{term}' ({len(rows)} shown):")
            for row in rows:
                print(f"  • {row[0]} at {row[1]} ({row[2]}) - {row[3]}")
