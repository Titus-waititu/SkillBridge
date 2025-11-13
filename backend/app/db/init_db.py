"""
Database initialization and seeding script.
Run this to set up the database with sample job postings and skills.
"""
from sqlalchemy import text
from app.db.database import engine, SessionLocal, Base
from app.db.models import JobPosting, Skill
from app.services.embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enable_pgvector():
    """Enable pgvector extension in PostgreSQL"""
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("✓ pgvector extension enabled")
        except Exception as e:
            logger.error(f"Error enabling pgvector: {e}")
            raise


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def seed_skills():
    """Seed the database with common tech skills"""
    logger.info("Seeding skills...")

    skills_data = [
        # Programming Languages
        ("Python", "Programming Languages",
         "High-level programming language for data science and web development"),
        ("JavaScript", "Programming Languages",
         "Essential for web development and frontend frameworks"),
        ("TypeScript", "Programming Languages", "Typed superset of JavaScript"),
        ("Java", "Programming Languages",
         "Enterprise-level object-oriented programming language"),
        ("Go", "Programming Languages", "Modern language for scalable systems"),
        ("Rust", "Programming Languages",
         "Systems programming language focused on safety"),
        ("C++", "Programming Languages", "High-performance systems programming"),

        # Frontend
        ("React", "Frontend", "Popular JavaScript library for building user interfaces"),
        ("Next.js", "Frontend", "React framework for production-grade applications"),
        ("Vue.js", "Frontend", "Progressive JavaScript framework"),
        ("Angular", "Frontend", "Platform for building web applications"),
        ("Tailwind CSS", "Frontend", "Utility-first CSS framework"),

        # Backend
        ("FastAPI", "Backend", "Modern Python web framework for APIs"),
        ("Node.js", "Backend", "JavaScript runtime for server-side development"),
        ("Django", "Backend", "High-level Python web framework"),
        ("Express.js", "Backend", "Minimal Node.js web framework"),
        ("Spring Boot", "Backend", "Java-based framework for microservices"),

        # Databases
        ("PostgreSQL", "Databases", "Advanced open-source relational database"),
        ("MongoDB", "Databases", "NoSQL document database"),
        ("Redis", "Databases", "In-memory data structure store"),
        ("MySQL", "Databases", "Popular relational database"),

        # Cloud & DevOps
        ("AWS", "Cloud", "Amazon Web Services cloud platform"),
        ("Azure", "Cloud", "Microsoft cloud computing platform"),
        ("Google Cloud", "Cloud", "Google's cloud platform"),
        ("Docker", "DevOps", "Containerization platform"),
        ("Kubernetes", "DevOps", "Container orchestration system"),
        ("CI/CD", "DevOps", "Continuous Integration and Deployment"),
        ("Terraform", "DevOps", "Infrastructure as Code tool"),

        # AI/ML
        ("Machine Learning", "AI/ML", "Algorithms that learn from data"),
        ("Deep Learning", "AI/ML", "Neural networks and advanced ML"),
        ("TensorFlow", "AI/ML", "Open-source ML framework"),
        ("PyTorch", "AI/ML", "Deep learning framework"),
        ("LLMs", "AI/ML", "Large Language Models"),
        ("RAG", "AI/ML", "Retrieval-Augmented Generation"),
        ("Vector Databases", "AI/ML", "Databases optimized for similarity search"),

        # Data
        ("Data Analysis", "Data", "Analyzing and interpreting data"),
        ("SQL", "Data", "Database query language"),
        ("Apache Spark", "Data", "Big data processing framework"),
        ("Pandas", "Data", "Python data manipulation library"),
        ("Data Visualization", "Data", "Presenting data graphically"),

        # Other
        ("Git", "Tools", "Version control system"),
        ("REST API", "Backend", "RESTful web services"),
        ("GraphQL", "Backend", "Query language for APIs"),
        ("Microservices", "Architecture", "Service-oriented architecture pattern"),
        ("System Design", "Architecture", "Designing scalable systems"),
    ]

    db = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        for name, category, description in skills_data:
            # Check if skill already exists
            existing = db.query(Skill).filter(Skill.name == name).first()
            if existing:
                logger.info(f"Skill already exists: {name}")
                continue

            # Generate embedding
            embedding = embedding_service.generate_embedding(name)

            # Create skill
            skill = Skill(
                name=name,
                category=category,
                description=description,
                embedding=embedding,
                demand_score=0.8,  # Default score
            )
            db.add(skill)
            logger.info(f"Added skill: {name}")

        db.commit()
        logger.info(f"✓ Seeded {len(skills_data)} skills")

    except Exception as e:
        logger.error(f"Error seeding skills: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_job_postings():
    """Seed the database with sample job postings"""
    logger.info("Seeding job postings...")

    jobs_data = [{"title": "Senior Software Engineer",
                  "company": "Tech Corp",
                  "location": "San Francisco, CA",
                  "salary_min": 150000,
                  "salary_max": 200000,
                  "required_skills": ["Python",
                                      "JavaScript",
                                      "React",
                                      "PostgreSQL",
                                      "Docker"],
                  "preferred_skills": ["Kubernetes",
                                       "AWS",
                                       "TypeScript"],
                  "experience_level": "Senior",
                  "remote_type": "Hybrid",
                  "description": "Build scalable web applications...",
                  },
                 {"title": "AI Engineer",
                  "company": "AI Innovations",
                  "location": "New York, NY",
                  "salary_min": 160000,
                  "salary_max": 220000,
                  "required_skills": ["Python",
                                      "Machine Learning",
                                      "TensorFlow",
                                      "PyTorch",
                                      "Docker"],
                  "preferred_skills": ["LLMs",
                                       "RAG",
                                       "Vector Databases",
                                       "AWS"],
                  "experience_level": "Senior",
                  "remote_type": "Remote",
                  "description": "Develop cutting-edge AI solutions...",
                  },
                 {"title": "Full Stack Developer",
                  "company": "StartupXYZ",
                  "location": "Austin, TX",
                  "salary_min": 120000,
                  "salary_max": 160000,
                  "required_skills": ["JavaScript",
                                      "React",
                                      "Node.js",
                                      "PostgreSQL"],
                  "preferred_skills": ["TypeScript",
                                       "Next.js",
                                       "Docker",
                                       "AWS"],
                  "experience_level": "Mid",
                  "remote_type": "Remote",
                  "description": "Join our fast-growing startup...",
                  },
                 {"title": "DevOps Engineer",
                  "company": "Cloud Solutions Inc",
                  "location": "Seattle, WA",
                  "salary_min": 140000,
                  "salary_max": 180000,
                  "required_skills": ["Docker",
                                      "Kubernetes",
                                      "AWS",
                                      "CI/CD",
                                      "Terraform"],
                  "preferred_skills": ["Python",
                                       "Go",
                                       "Monitoring"],
                  "experience_level": "Senior",
                  "remote_type": "Hybrid",
                  "description": "Manage cloud infrastructure...",
                  },
                 {"title": "Data Scientist",
                  "company": "Data Insights Co",
                  "location": "Boston, MA",
                  "salary_min": 130000,
                  "salary_max": 170000,
                  "required_skills": ["Python",
                                      "SQL",
                                      "Machine Learning",
                                      "Pandas",
                                      "Data Visualization"],
                  "preferred_skills": ["Deep Learning",
                                       "Apache Spark",
                                       "AWS"],
                  "experience_level": "Mid",
                  "remote_type": "Remote",
                  "description": "Analyze complex datasets...",
                  },
                 ]

    db = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        for job_data in jobs_data:
            # Generate embedding from skills
            all_skills = job_data["required_skills"] + \
                job_data["preferred_skills"]
            skills_text = ", ".join(all_skills)
            embedding = embedding_service.generate_embedding(skills_text)

            # Create job posting
            job = JobPosting(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                description=job_data["description"],
                required_skills=job_data["required_skills"],
                preferred_skills=job_data["preferred_skills"],
                experience_level=job_data["experience_level"],
                remote_type=job_data["remote_type"],
                skills_embedding=embedding,
            )
            db.add(job)
            logger.info(
                f"Added job: {
                    job_data['title']} at {
                    job_data['company']}")

        db.commit()
        logger.info(f"✓ Seeded {len(jobs_data)} job postings")

    except Exception as e:
        logger.error(f"Error seeding job postings: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Run all initialization steps"""
    logger.info("🚀 Starting database initialization...")

    try:
        # Enable pgvector extension
        enable_pgvector()

        # Create tables
        create_tables()

        # Seed data
        seed_skills()
        seed_job_postings()

        logger.info("✅ Database initialization complete!")

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
