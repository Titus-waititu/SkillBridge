import google.generativeai as genai
from app.core.config import settings
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google's Gemini API"""

    def __init__(self):
        """Initialize Gemini API client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
        logger.info(
            "Gemini API client initialized with gemini-2.5-flash-preview-09-2025")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_content(
            self,
            prompt: str,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None) -> str:
        """
        Generate content using Gemini API with retry logic.

        Args:
            prompt: The prompt to send to Gemini
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            logger.info("Sending request to Gemini API")

            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Generate content
            response = self.model.generate_content(
                prompt, generation_config=generation_config
            )

            # Extract text from response
            if response.text:
                logger.info("Successfully generated content from Gemini")
                return response.text
            else:
                logger.error("Empty response from Gemini API")
                raise ValueError("Empty response from Gemini API")

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise

    async def generate_roadmap(
        self,
        current_skills: list[str],
        target_role: str,
        skill_gaps: list[str],
        recommended_skills: list[str],
        target_salary: Optional[float] = None,
        experience_years: Optional[float] = None,
    ) -> str:
        """
        Generate a personalized career roadmap using Gemini.

        Args:
            current_skills: List of user's current skills
            target_role: Target job role
            skill_gaps: Skills the user needs to learn
            recommended_skills: Additional recommended skills
            target_salary: Target salary (optional)
            experience_years: Years of experience (optional)

        Returns:
            JSON string containing the learning roadmap
        """
        salary_context = (
            f"Target Salary: ${target_salary:,.0f} per year" if target_salary else "")
        experience_context = (
            f"Current Experience: {experience_years} years" if experience_years else "")

        prompt = f"""
You are an expert career coach specializing in tech career development. Generate a detailed, actionable learning roadmap for a professional transitioning to a {target_role} role.

**Current Profile:**
- Current Skills: {', '.join(current_skills)}
- {experience_context}
- {salary_context}

**Target Role:** {target_role}

**Skills to Learn:** {', '.join(skill_gaps[:10])}

**Additional Recommended Skills:** {', '.join(recommended_skills[:5])}

**Task:** Create a comprehensive, step-by-step learning path with 5-8 major milestones. Each step should build upon the previous one and lead the learner progressively toward the target role.

For each step, provide:
1. **title**: A clear, motivating title (e.g., "Master the Fundamentals")
2. **description**: Detailed explanation of what to learn, why it matters, and how it applies to the target role (2-3 paragraphs)
3. **estimated_duration**: Realistic time estimate (e.g., "2-3 weeks", "1 month")
4. **resources**: 3-5 specific learning resources (online courses, books, documentation, YouTube channels, practice platforms)
5. **skills_gained**: List of 2-4 specific skills that will be mastered in this step

**Output Format:** Return ONLY a valid JSON array with this exact structure (no additional text):

[
  {{
    "step": 1,
    "title": "Foundation Building: Core Concepts",
    "description": "Begin your journey by establishing a solid foundation...",
    "estimated_duration": "2-3 weeks",
    "resources": [
      "Course: Introduction to X on Coursera",
      "Book: 'Learning X' by Author Name",
      "Practice: LeetCode Easy Problems"
    ],
    "skills_gained": ["Skill A", "Skill B", "Skill C"]
  }}
]

Make the roadmap practical, achievable, and tailored to the specific transition from the current skills to the target role. Focus on real-world applicability and industry best practices.
"""

        return await self.generate_content(prompt, temperature=0.8)

    async def analyze_skill_gap(
        self, current_skills: list[str], required_skills: list[str]
    ) -> dict:
        """
        Analyze the gap between current and required skills.

        Args:
            current_skills: User's current skills
            required_skills: Required skills for target role

        Returns:
            Analysis of skill gaps with priorities
        """
        prompt = f"""
Analyze the skill gap for a professional looking to acquire new skills.

Current Skills: {', '.join(current_skills)}
Required Skills: {', '.join(required_skills)}

Provide:
1. Priority skills to learn first (in order of importance)
2. Estimated difficulty for each skill (Easy/Medium/Hard)
3. Dependencies between skills
4. Approximate time to competency for each skill

Format as JSON:
{{
  "priority_skills": [
    {{
      "skill": "Skill name",
      "priority": 1,
      "difficulty": "Medium",
      "time_to_competency": "2-3 months",
      "prerequisites": ["Skill A", "Skill B"]
    }}
  ],
  "learning_sequence": ["Skill 1", "Skill 2", "Skill 3"]
}}
"""

        response = await self.generate_content(prompt, temperature=0.5)

        try:
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse skill gap analysis JSON")
            return {"priority_skills": [], "learning_sequence": []}
