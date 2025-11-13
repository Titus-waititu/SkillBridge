from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Skill
from app.api.schemas import (
    SkillCreate,
    SkillResponse,
    SkillSearchRequest,
    SkillSearchResult,
)
from app.services.embedding_service import EmbeddingService

router = APIRouter()


@router.post("/", response_model=SkillResponse)
async def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    """Create a new skill with embedding"""
    # Check if skill already exists
    existing_skill = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing_skill:
        raise HTTPException(status_code=400, detail="Skill already exists")

    # Generate embedding
    embedding_service = EmbeddingService()
    embedding = embedding_service.generate_embedding(skill.name)

    # Create skill
    db_skill = Skill(
        name=skill.name,
        category=skill.category,
        description=skill.description,
        embedding=embedding,
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)

    return db_skill


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
        skip: int = 0,
        limit: int = 50,
        category: str = None,
        db: Session = Depends(get_db)):
    """List all skills with optional filtering"""
    query = db.query(Skill)

    if category:
        query = query.filter(Skill.category == category)

    skills = query.offset(skip).limit(limit).all()
    return skills


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get a specific skill by ID"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/search", response_model=List[SkillSearchResult])
async def search_skills(
    request: SkillSearchRequest, db: Session = Depends(get_db)
):
    """Search for skills using vector similarity"""
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.generate_embedding(request.query)

    # Perform vector similarity search
    results = (
        db.query(
            Skill.name,
            Skill.category,
            Skill.demand_score,
            Skill.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .order_by("distance")
        .limit(request.limit)
        .all()
    )

    # Convert to response format
    search_results = []
    for result in results:
        # Count jobs requiring this skill (placeholder)
        job_count = 0  # TODO: Implement actual count from job_postings

        search_results.append(
            SkillSearchResult(
                skill_name=result.name,
                category=result.category or "Uncategorized",
                similarity_score=1 - result.distance,  # Convert distance to similarity
                demand_score=result.demand_score,
                job_count=job_count,
            )
        )

    return search_results


@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    """Get all unique skill categories"""
    categories = db.query(Skill.category).distinct().all()
    return {"categories": [cat[0] for cat in categories if cat[0]]}


@router.get("/trending/top")
async def get_trending_skills(limit: int = 10, db: Session = Depends(get_db)):
    """Get top trending skills based on demand score"""
    skills = (
        db.query(Skill)
        .filter(Skill.demand_score.isnot(None))
        .order_by(Skill.demand_score.desc())
        .limit(limit)
        .all()
    )
    return skills
