"""
Load Kaggle LinkedIn job postings data into the database.
This script processes the large postings.csv file in batches and creates
proper embeddings for vector search.
"""
from app.services.embedding_service import EmbeddingService
from app.db.models import JobPosting, Skill
from app.db.database import SessionLocal, engine
import sys
import os
import pandas as pd
import logging
from sqlalchemy import text
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_salary(row):
    """Extract salary information from various fields"""
    if pd.notna(row.get('normalized_salary')):
        return row['normalized_salary']
    if pd.notna(row.get('max_salary')):
        return row['max_salary']
    if pd.notna(row.get('med_salary')):
        return row['med_salary']
    return None


def extract_skills_from_desc(skills_desc: str) -> list:
    """Extract skills from the skills_desc field"""
    if pd.isna(skills_desc) or not skills_desc:
        return []

    # Split by common delimiters
    skills = []
    for delimiter in [',', ';', '|', '\n']:
        if delimiter in str(skills_desc):
            skills = [s.strip() for s in str(skills_desc).split(delimiter)]
            break

    # If no delimiters found, return as single skill
    if not skills:
        skills = [str(skills_desc).strip()]

    # Filter out empty and very long strings (likely not skills)
    skills = [s for s in skills if s and len(s) < 50]
    return skills[:10]  # Limit to 10 skills per job


def load_kaggle_jobs(batch_size=1000, max_jobs=5000):
    """
    Load jobs from Kaggle CSV in batches.

    Args:
        batch_size: Number of rows to process at once
        max_jobs: Maximum number of jobs to load (to avoid overwhelming the DB)
    """
    logger.info("🚀 Starting Kaggle job data import...")

    db = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        # Load skills mapping for reference
        skills_mapping = {}
        skills_file = "archive/mappings/skills.csv"
        if os.path.exists(skills_file):
            skills_df = pd.read_csv(skills_file)
            skills_mapping = dict(
                zip(skills_df['skill_abr'], skills_df['skill_name']))
            logger.info(f"Loaded {len(skills_mapping)} skill mappings")

        # Load job postings in chunks
        csv_file = "archive/postings.csv"
        if not os.path.exists(csv_file):
            logger.error(f"File not found: {csv_file}")
            return

        logger.info(f"Reading {csv_file}...")

        # Read CSV in chunks to handle large file
        chunk_iterator = pd.read_csv(
            csv_file,
            chunksize=batch_size,
            low_memory=False,
            encoding='utf-8',
            on_bad_lines='skip'
        )

        total_loaded = 0
        total_skipped = 0

        for chunk_num, chunk in enumerate(chunk_iterator, 1):
            if total_loaded >= max_jobs:
                logger.info(f"Reached max jobs limit ({max_jobs}). Stopping.")
                break

            logger.info(f"Processing batch {chunk_num} ({len(chunk)} rows)...")

            for idx, row in tqdm(chunk.iterrows(), total=len(
                    chunk), desc=f"Batch {chunk_num}"):
                try:
                    # Skip if missing critical fields
                    if pd.isna(
                            row.get('title')) or pd.isna(
                            row.get('description')):
                        total_skipped += 1
                        continue

                    # Extract fields
                    title = str(row['title']).strip()[
                        :200]  # Limit title length
                    company = str(row.get('company_name', 'Unknown'))[
                        :200] if pd.notna(row.get('company_name')) else 'Unknown'
                    description = str(row['description'])[
                        :5000]  # Limit description length
                    location = str(row.get('location', ''))[
                        :200] if pd.notna(row.get('location')) else None

                    # Extract skills
                    skills = extract_skills_from_desc(row.get('skills_desc'))

                    # Get salary info
                    max_salary = clean_salary(row)
                    min_salary = row.get('min_salary') if pd.notna(
                        row.get('min_salary')) else None

                    # Determine experience level
                    experience_level = 'Mid'  # Default
                    if pd.notna(row.get('formatted_experience_level')):
                        exp = str(row['formatted_experience_level']).lower()
                        if 'entry' in exp or 'junior' in exp:
                            experience_level = 'Entry'
                        elif 'senior' in exp or 'lead' in exp or 'principal' in exp:
                            experience_level = 'Senior'
                        elif 'director' in exp or 'executive' in exp:
                            experience_level = 'Executive'

                    # Determine remote type
                    remote_type = 'On-site'
                    if pd.notna(row.get('remote_allowed')):
                        if str(
                                row['remote_allowed']) == '1' or str(
                                row['remote_allowed']).lower() == 'true':
                            remote_type = 'Remote'

                    # Create embedding from title + description + skills
                    embedding_text = f"{title}. {
                        description[
                            :500]}. Skills: {
                        ', '.join(skills)}"
                    embedding = embedding_service.generate_embedding(
                        embedding_text)

                    # Create job posting
                    job = JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        salary_min=min_salary,
                        salary_max=max_salary,
                        description=description,
                        required_skills=skills,
                        experience_level=experience_level,
                        remote_type=remote_type,
                        skills_embedding=embedding,
                        source_url=str(
                            row.get(
                                'job_posting_url',
                                '')) if pd.notna(
                            row.get('job_posting_url')) else None,
                    )

                    db.add(job)
                    total_loaded += 1

                    # Commit every 100 jobs
                    if total_loaded % 100 == 0:
                        db.commit()
                        logger.info(f"✓ Loaded {total_loaded} jobs so far...")

                    # Stop if we reached max
                    if total_loaded >= max_jobs:
                        break

                except Exception as e:
                    logger.warning(f"Error processing row {idx}: {str(e)}")
                    total_skipped += 1
                    continue

            # Commit remaining jobs
            db.commit()

            if total_loaded >= max_jobs:
                break

        logger.info(f"""
        ✅ Kaggle data import complete!
        - Total jobs loaded: {total_loaded}
        - Total skipped: {total_skipped}
        """)

    except Exception as e:
        logger.error(f"❌ Error loading Kaggle data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Load Kaggle LinkedIn job data')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for processing')
    parser.add_argument(
        '--max-jobs',
        type=int,
        default=5000,
        help='Maximum jobs to load')

    args = parser.parse_args()

    load_kaggle_jobs(batch_size=args.batch_size, max_jobs=args.max_jobs)
