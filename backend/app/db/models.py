from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.db.database import Base


class JobPosting(Base):
    """Job posting model with vector embeddings for skills"""

    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    company = Column(String, index=True)
    location = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    description = Column(Text)
    required_skills = Column(ARRAY(String))
    preferred_skills = Column(ARRAY(String))
    experience_level = Column(String)  # Junior, Mid, Senior, Lead
    remote_type = Column(String)  # Remote, Hybrid, Onsite

    # Vector embedding for semantic search
    skills_embedding = Column(Vector(384))  # Dimension matches EMBEDDING_MODEL

    # Metadata
    source_url = Column(String)
    posted_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    # Create index for vector similarity search
    __table_args__ = (
        Index(
            "idx_skills_embedding",
            skills_embedding,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"skills_embedding": "vector_cosine_ops"},
        ),
    )


class UserProfile(Base):
    """User profile with current skills"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    current_role = Column(String)
    current_skills = Column(ARRAY(String))
    experience_years = Column(Float)

    # Vector embedding for user skills
    skills_embedding = Column(Vector(384))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)


class CareerRoadmap(Base):
    """Generated career roadmaps"""

    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    # Input data
    current_skills = Column(ARRAY(String))
    target_role = Column(String, index=True)
    target_salary = Column(Float)

    # Output data
    skill_gaps = Column(ARRAY(String))
    recommended_skills = Column(ARRAY(String))
    learning_path = Column(JSON)  # Detailed step-by-step roadmap
    estimated_timeline = Column(String)

    # Metadata
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Skill(Base):
    """Skill taxonomy with vector embeddings"""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True)  # Programming, DevOps, Cloud, etc.
    description = Column(Text)

    # Popularity metrics
    demand_score = Column(Float)  # Based on job posting frequency
    avg_salary_impact = Column(Float)

    # Vector embedding
    embedding = Column(Vector(384))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
