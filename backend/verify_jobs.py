"""Quick script to verify Kaggle job data was loaded"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys
sys.path.append("app")


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Count total jobs
    result = conn.execute(text("SELECT COUNT(*) FROM job_postings"))
    total = result.scalar()
    print(f"\n✅ Total jobs in database: {total}")

    # Get sample jobs
    result = conn.execute(text("""
        SELECT title, company, location, experience_level, remote_type, salary_min, salary_max
        FROM job_postings
        ORDER BY created_at DESC
        LIMIT 10
    """))

    print("\n📋 Sample of most recently loaded jobs:\n")
    for row in result:
        salary_info = ""
        if row[5] or row[6]:  # salary_min or salary_max
            if row[5] and row[6]:
                salary_info = f" (${row[5]:,.0f} - ${row[6]:,.0f})"
            elif row[6]:
                salary_info = f" (up to ${row[6]:,.0f})"
            elif row[5]:
                salary_info = f" (from ${row[5]:,.0f})"

        print(f"  • {row[0]} at {row[1]}")
        print(f"    📍 {row[2]} | 💼 {row[3]} | 🏠 {row[4]}{salary_info}")
        print()

    # Check experience level distribution
    result = conn.execute(text("""
        SELECT experience_level, COUNT(*) as count
        FROM job_postings
        GROUP BY experience_level
        ORDER BY count DESC
    """))

    print("\n📊 Experience level distribution:")
    for row in result:
        print(f"  • {row[0]}: {row[1]} jobs")

    # Check remote type distribution
    result = conn.execute(text("""
        SELECT remote_type, COUNT(*) as count
        FROM job_postings
        GROUP BY remote_type
        ORDER BY count DESC
    """))

    print("\n🏠 Remote type distribution:")
    for row in result:
        print(f"  • {row[0]}: {row[1]} jobs")

print("\n✅ Database verification complete!\n")
