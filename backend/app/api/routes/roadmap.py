from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import CareerRoadmap, JobPosting
from app.api.schemas import RoadmapRequest, RoadmapResponse, LearningStep
from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(
    request: RoadmapRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Generate a personalized career roadmap using RAG and LLM.

    This endpoint:
    1. Creates embeddings from user's current skills
    2. Queries vector database for matching job postings
    3. Identifies skill gaps
    4. Uses Gemini API to generate detailed learning path
    """
    try:
        logger.info(
            f"Generating roadmap for target role: {request.target_role}"
        )

        # Step 1: Generate embedding service
        embedding_service = EmbeddingService()

        # Step 2: Find relevant job postings using vector search
        target_role_embedding = embedding_service.generate_embedding(
            request.target_role)

        # First try to find jobs with matching title
        similar_jobs = (
            db.query(
                JobPosting,
                JobPosting.skills_embedding.cosine_distance(target_role_embedding).label(
                    "distance"
                ),
            )
            .filter(JobPosting.title.ilike(f"%{request.target_role}%"))
            .order_by("distance")
            .limit(10)
            .all()
        )

        # If no exact title matches, use vector similarity alone
        if not similar_jobs:
            logger.info(
                f"No exact title matches for '{request.target_role}', using vector similarity")
            similar_jobs = (
                db.query(
                    JobPosting,
                    JobPosting.skills_embedding.cosine_distance(target_role_embedding).label(
                        "distance"
                    ),
                )
                .order_by("distance")
                .limit(5)
                .all()
            )

        if not similar_jobs:
            raise HTTPException(
                status_code=404,
                detail=f"No job postings found in database",
            )

        # Step 3: Extract required skills from top matching jobs
        all_required_skills = set()
        all_preferred_skills = set()

        for job, _ in similar_jobs:
            if job.required_skills:
                all_required_skills.update(job.required_skills)
            if job.preferred_skills:
                all_preferred_skills.update(job.preferred_skills)

        # Step 4: Identify skill gaps
        current_skills_set = set(skill.lower()
                                 for skill in request.current_skills)
        skill_gaps = [
            skill
            for skill in all_required_skills
            if skill.lower() not in current_skills_set
        ]
        recommended_skills = list(all_preferred_skills - current_skills_set)

        logger.info(f"Identified {len(skill_gaps)} skill gaps")

        # Step 5: Generate detailed roadmap using Gemini
        gemini_service = GeminiService()

        prompt = f"""
        Generate a detailed, step-by-step learning roadmap for a professional transitioning to a {request.target_role} role.

        Current Skills: {', '.join(request.current_skills)}
        Target Role: {request.target_role}
        Target Salary: ${request.target_salary:,.0f} per year (if applicable)
        Experience: {request.experience_years} years

        Required Skills to Learn: {', '.join(skill_gaps[:10])}
        Recommended Additional Skills: {', '.join(recommended_skills[:5])}

        Create a personalized learning path with 5-8 major steps. For each step, provide:
        1. A clear title
        2. Detailed description of what to learn and why
        3. Estimated duration (e.g., "2-3 weeks", "1 month")
        4. Specific learning resources (courses, books, projects)
        5. Skills that will be gained

        Format the response as a JSON array of steps with this structure:
        [
            {{
                "step": 1,
                "title": "Step title",
                "description": "Detailed description",
                "estimated_duration": "2 weeks",
                "resources": ["Resource 1", "Resource 2"],
                "skills_gained": ["Skill 1", "Skill 2"]
            }}
        ]

        Provide only the JSON array, no additional text.
        """

        learning_path_json = await gemini_service.generate_content(prompt)

        # Parse the learning path
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', learning_path_json, re.DOTALL)
            if json_match:
                learning_path_data = json.loads(json_match.group())
            else:
                learning_path_data = json.loads(learning_path_json)

            learning_path = [LearningStep(**step)
                             for step in learning_path_data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse learning path JSON: {e}")
            # Fallback to basic structure
            learning_path = [
                LearningStep(
                    step=1,
                    title="Foundation Building",
                    description=f"Start by learning the core skills: {', '.join(skill_gaps[:3])}",
                    estimated_duration="1-2 months",
                    resources=["Online courses", "Documentation", "Practice projects"],
                    skills_gained=skill_gaps[:3],
                )
            ]

        # Calculate estimated timeline
        total_duration = sum(
            [
                int(step.estimated_duration.split()[0])
                for step in learning_path
                if step.estimated_duration.split()[0].isdigit()
            ]
        )
        estimated_timeline = f"{total_duration} weeks" if total_duration < 52 else f"{total_duration // 4} months"

        # Calculate confidence score based on skill overlap
        confidence_score = (
            len(current_skills_set & all_required_skills) / len(all_required_skills)
            if all_required_skills
            else 0.0
        )

        # Step 6: Save roadmap to database
        roadmap = CareerRoadmap(
            current_skills=request.current_skills,
            target_role=request.target_role,
            target_salary=request.target_salary,
            skill_gaps=list(skill_gaps),
            recommended_skills=recommended_skills,
            learning_path=[step.dict() for step in learning_path],
            estimated_timeline=estimated_timeline,
            confidence_score=confidence_score,
        )

        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)

        logger.info(f"Roadmap generated successfully with ID: {roadmap.id}")

        # Convert to response format
        return RoadmapResponse(
            id=roadmap.id,
            target_role=roadmap.target_role,
            current_skills=roadmap.current_skills,
            skill_gaps=roadmap.skill_gaps,
            recommended_skills=roadmap.recommended_skills,
            learning_path=learning_path,
            estimated_timeline=roadmap.estimated_timeline,
            confidence_score=roadmap.confidence_score,
            created_at=roadmap.created_at,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
        # Return user-friendly error message
        error_message = str(e)
        if "API key" in error_message.lower():
            detail = "AI service configuration error. Please check API key settings."
        elif "database" in error_message.lower() or "connection" in error_message.lower():
            detail = "Database connection error. Please try again later."
        elif "timeout" in error_message.lower():
            detail = "Request timed out. Please try again with fewer skills or a simpler role."
        else:
            detail = f"Unable to generate roadmap. Please try again or contact support. Error: {error_message[:100]}"

        raise HTTPException(status_code=500, detail=detail)


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    """Get a specific roadmap by ID"""
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == roadmap_id).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    # Convert learning_path from JSON to LearningStep objects
    learning_path = [LearningStep(**step) for step in roadmap.learning_path]

    return RoadmapResponse(
        id=roadmap.id,
        target_role=roadmap.target_role,
        current_skills=roadmap.current_skills,
        skill_gaps=roadmap.skill_gaps,
        recommended_skills=roadmap.recommended_skills,
        learning_path=learning_path,
        estimated_timeline=roadmap.estimated_timeline,
        confidence_score=roadmap.confidence_score,
        created_at=roadmap.created_at,
    )


@router.get("/user/{user_id}")
async def get_user_roadmaps(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Get all roadmaps for a specific user"""
    roadmaps = (
        db.query(CareerRoadmap)
        .filter(CareerRoadmap.user_id == user_id)
        .order_by(CareerRoadmap.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return roadmaps
