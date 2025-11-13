from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import JobPosting
from app.api.schemas import (
    JobPostingCreate,
    JobPostingResponse,
    JobMatchRequest,
    JobMatchResult,
)
from app.services.embedding_service import EmbeddingService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=JobPostingResponse)
async def create_job_posting(
        job: JobPostingCreate,
        db: Session = Depends(get_db)):
    """Create a new job posting with skill embeddings"""
    try:
        # Generate embedding from required skills
        embedding_service = EmbeddingService()
        all_skills = job.required_skills + job.preferred_skills
        skills_text = ", ".join(all_skills) if all_skills else job.title
        skills_embedding = embedding_service.generate_embedding(skills_text)

        # Create job posting
        db_job = JobPosting(
            title=job.title,
            company=job.company,
            location=job.location,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            description=job.description,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            experience_level=job.experience_level,
            remote_type=job.remote_type,
            skills_embedding=skills_embedding,
            source_url=job.source_url,
            posted_date=job.posted_date,
        )

        db.add(db_job)
        db.commit()
        db.refresh(db_job)

        logger.info(f"Created job posting: {db_job.id} - {db_job.title}")
        return db_job

    except Exception as e:
        logger.error(f"Error creating job posting: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create job posting: {
                str(e)}")


@router.get("/", response_model=List[JobPostingResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    experience_level: str = None,
    remote_type: str = None,
    db: Session = Depends(get_db),
):
    """List job postings with optional filtering"""
    query = db.query(JobPosting)

    if experience_level:
        query = query.filter(JobPosting.experience_level == experience_level)
    if remote_type:
        query = query.filter(JobPosting.remote_type == remote_type)

    jobs = query.order_by(JobPosting.created_at.desc()
                          ).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job posting by ID"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.post("/match", response_model=List[JobMatchResult])
async def match_jobs(request: JobMatchRequest, db: Session = Depends(get_db)):
    """
    Find job postings that match user's skills using vector similarity.
    Returns jobs ranked by match score with identified skill gaps.
    """
    try:
        # Generate embedding from user skills
        embedding_service = EmbeddingService()
        skills_text = ", ".join(request.skills)
        user_skills_embedding = embedding_service.generate_embedding(
            skills_text)

        # Build query
        query = db.query(JobPosting, JobPosting.skills_embedding.cosine_distance(
            user_skills_embedding).label("distance"), )

        # Apply filters
        if request.min_salary:
            query = query.filter(JobPosting.salary_min >= request.min_salary)
        if request.experience_level:
            query = query.filter(
                JobPosting.experience_level == request.experience_level)
        if request.remote_type:
            query = query.filter(JobPosting.remote_type == request.remote_type)

        # Execute query
        results = query.order_by("distance").limit(request.limit).all()

        # Convert to response format
        user_skills_set = set(skill.lower() for skill in request.skills)
        match_results = []

        for job, distance in results:
            # Calculate match score (1 - distance = similarity)
            match_score = 1 - distance

            # Identify missing skills
            required_skills_set = set(
                skill.lower() for skill in (job.required_skills or [])
            )
            missing_skills = list(required_skills_set - user_skills_set)

            match_results.append(
                JobMatchResult(
                    job_id=job.id,
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    required_skills=job.required_skills or [],
                    match_score=round(match_score, 3),
                    missing_skills=missing_skills,
                )
            )

        logger.info(f"Found {len(match_results)} matching jobs")
        return match_results

    except Exception as e:
        logger.error(f"Error matching jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to match jobs: {
                str(e)}")


@router.get("/stats/summary")
async def get_job_stats(db: Session = Depends(get_db)):
    """Get summary statistics about job postings"""
    from sqlalchemy import func

    total_jobs = db.query(func.count(JobPosting.id)).scalar()

    # Jobs by experience level
    by_experience = (
        db.query(JobPosting.experience_level, func.count(JobPosting.id))
        .group_by(JobPosting.experience_level)
        .all()
    )

    # Jobs by remote type
    by_remote = (
        db.query(JobPosting.remote_type, func.count(JobPosting.id))
        .group_by(JobPosting.remote_type)
        .all()
    )

    # Average salary range
    avg_salary_min = db.query(func.avg(JobPosting.salary_min)).scalar()
    avg_salary_max = db.query(func.avg(JobPosting.salary_max)).scalar()

    return {
        "total_jobs": total_jobs,
        "by_experience_level": dict(by_experience),
        "by_remote_type": dict(by_remote),
        "average_salary_range": {
            "min": round(avg_salary_min, 2) if avg_salary_min else None,
            "max": round(avg_salary_max, 2) if avg_salary_max else None,
        },
    }
