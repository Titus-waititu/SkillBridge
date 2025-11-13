from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class SkillBase(BaseModel):
    """Base skill schema"""

    name: str
    category: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for creating a skill"""

    description: Optional[str] = None


class SkillResponse(SkillBase):
    """Schema for skill response"""

    id: int
    demand_score: Optional[float] = None
    avg_salary_impact: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobPostingBase(BaseModel):
    """Base job posting schema"""

    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_level: Optional[str] = None
    remote_type: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    """Schema for creating a job posting"""

    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None


class JobPostingResponse(JobPostingBase):
    """Schema for job posting response"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapRequest(BaseModel):
    """Schema for roadmap generation request"""

    current_skills: List[str] = Field(...,
                                      min_items=1,
                                      description="List of current skills")
    target_role: str = Field(..., description="Desired job role")
    target_salary: Optional[float] = Field(
        None, description="Target salary in USD")
    experience_years: Optional[float] = Field(
        None, description="Years of experience")


class LearningStep(BaseModel):
    """Individual learning step in roadmap"""

    step: int
    title: str
    description: str
    estimated_duration: str
    resources: List[str] = []
    skills_gained: List[str] = []


class RoadmapResponse(BaseModel):
    """Schema for roadmap generation response"""

    id: int
    target_role: str
    current_skills: List[str]
    skill_gaps: List[str]
    recommended_skills: List[str]
    learning_path: List[LearningStep]
    estimated_timeline: str
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class SkillSearchRequest(BaseModel):
    """Schema for skill search request"""

    query: str = Field(..., description="Search query for skills")
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of results to return")


class SkillSearchResult(BaseModel):
    """Schema for skill search result"""

    skill_name: str
    category: str
    similarity_score: float
    demand_score: Optional[float] = None
    job_count: int


class JobMatchRequest(BaseModel):
    """Schema for job matching request"""

    skills: List[str] = Field(..., min_items=1,
                              description="Skills to match against jobs")
    limit: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of results to return")
    min_salary: Optional[float] = None
    experience_level: Optional[str] = None
    remote_type: Optional[str] = None


class JobMatchResult(BaseModel):
    """Schema for job match result"""

    job_id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    required_skills: List[str]
    match_score: float
    missing_skills: List[str]


class UserProfileCreate(BaseModel):
    """Schema for creating user profile"""

    email: EmailStr
    name: Optional[str] = None
    current_role: Optional[str] = None
    current_skills: List[str] = []
    experience_years: Optional[float] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""

    id: int
    email: str
    name: Optional[str]
    current_role: Optional[str]
    current_skills: List[str]
    experience_years: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
