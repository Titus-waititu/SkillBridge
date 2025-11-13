# Skill Coach Backend

AI-Powered Career Path Navigator using RAG (Retrieval-Augmented Generation) and Vector Search.

## Features

- 🎯 **Personalized Career Roadmaps** - Generate custom learning paths based on your skills and goals
- 🔍 **Vector-Based Job Matching** - Find jobs that match your skillset using semantic search
- 🤖 **AI-Powered Guidance** - Leverage Gemini API for intelligent career advice
- 📊 **Skills Analysis** - Track trending skills and their market demand
- 💾 **PostgreSQL + pgvector** - Advanced vector database for similarity search

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with pgvector extension
- **AI/ML**:
  - Google Gemini API for content generation
  - Sentence Transformers for embeddings
- **Cache**: Redis
- **Task Queue**: Celery

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Redis (optional, for background tasks)
- Google Gemini API key

## Installation

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/skill_coach
GEMINI_API_KEY=your_actual_gemini_api_key
REDIS_URL=redis://localhost:6379/0
```

### 5. Setup PostgreSQL with pgvector

**Install pgvector:**

```sql
CREATE EXTENSION vector;
```

**Create Database:**

```sql
CREATE DATABASE skill_coach;
```

### 6. Initialize Database

Run the initialization script to create tables and seed data:

```bash
python -m app.db.init_db
```

## Running the API

### Development Mode

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Skills

- `GET /api/v1/skills/` - List all skills
- `POST /api/v1/skills/` - Create a new skill
- `POST /api/v1/skills/search` - Search skills using vector similarity
- `GET /api/v1/skills/trending/top` - Get top trending skills

### Jobs

- `GET /api/v1/jobs/` - List job postings
- `POST /api/v1/jobs/` - Create a job posting
- `POST /api/v1/jobs/match` - Find matching jobs for user skills
- `GET /api/v1/jobs/stats/summary` - Get job statistics

### Roadmap

- `POST /api/v1/roadmap/generate` - Generate personalized career roadmap
- `GET /api/v1/roadmap/{roadmap_id}` - Get a specific roadmap
- `GET /api/v1/roadmap/user/{user_id}` - Get all roadmaps for a user

## Example Request

### Generate Career Roadmap

```bash
curl -X POST "http://localhost:8000/api/v1/roadmap/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_skills": ["Python", "JavaScript", "React"],
    "target_role": "AI Engineer",
    "target_salary": 180000,
    "experience_years": 3
  }'
```

### Match Jobs to Skills

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/match" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "limit": 10,
    "min_salary": 120000
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── skills.py      # Skills endpoints
│   │   │   ├── jobs.py        # Jobs endpoints
│   │   │   └── roadmap.py     # Roadmap generation
│   │   └── schemas.py         # Pydantic models
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── db/
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   └── init_db.py         # Database initialization
│   └── services/
│       ├── embedding_service.py   # Vector embeddings
│       └── gemini_service.py      # Gemini API integration
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
└── .env.example              # Environment variables template
```

## How It Works

### RAG Pipeline

1. **Data Ingestion**: Job postings are stored with their skill requirements converted to vector embeddings
2. **Query Processing**: User's current skills are converted to embeddings
3. **Vector Search**: pgvector finds the most similar job postings using cosine similarity
4. **Skill Gap Analysis**: Identifies missing skills by comparing user skills vs. job requirements
5. **LLM Generation**: Gemini API creates a personalized learning roadmap based on the gap analysis

### Vector Search Architecture

```
User Skills → Embedding Model → Vector (384D)
                                    ↓
                              Vector Search
                                    ↓
Job Postings (with embeddings) → Top Matches → Skill Gaps
                                                     ↓
                                              Gemini API
                                                     ↓
                                          Learning Roadmap
```

## Development

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Deployment

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### pgvector Extension Not Found

Make sure pgvector is installed in your PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Gemini API Errors

- Verify your API key is correct
- Check your API quota and rate limits
- Ensure you have enabled the Gemini API in Google Cloud Console

### Embedding Model Download

The first run will download the sentence-transformers model (~80MB). This is normal and happens once.

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
