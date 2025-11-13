# 🚀 Skill Coach - AI-Powered Career Path Navigator

An advanced full-stack application that leverages **RAG (Retrieval-Augmented Generation)** and **Vector Databases** to provide personalized, data-driven career roadmaps for tech professionals.

![Tech Stack](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-blue) ![Gemini](https://img.shields.io/badge/Gemini-AI-orange)

## 📋 Problem Statement

The current job search process is generic and frustrating. Professionals struggle to:

- **Identify exact skill gaps** between their current role and dream role
- Find **personalized learning paths** based on real market data
- Understand which skills are **actually in-demand** in the job market
- Get **actionable, step-by-step guidance** for career transitions

## 💡 Solution

Skill Coach solves these problems by:

1. **Data-Driven Analysis**: Analyzes real job postings (scraped or mocked) to identify in-demand skills
2. **Vector Search**: Uses pgvector for semantic similarity matching between your skills and job requirements
3. **AI-Powered Roadmaps**: Leverages Google's Gemini API to generate personalized, step-by-step learning paths
4. **RAG Architecture**: Combines vector database retrieval with LLM generation for contextually relevant recommendations

### How It Works

```
User Input → Vector Embedding → Database Query → Skill Gap Analysis → LLM Generation → Personalized Roadmap
```

1. User provides current skills and target role
2. System converts skills to vector embeddings
3. Vector database finds similar job postings using cosine similarity
4. Identifies skill gaps by comparing user skills vs. job requirements
5. Gemini API generates detailed learning roadmap based on gaps
6. Returns actionable, step-by-step path with resources and timelines

## 🛠️ Tech Stack

| Component            | Technology                                     | Why It's In-Demand                                                              |
| -------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| **Frontend**         | Next.js 14 (React) + TypeScript + Tailwind CSS | Industry standard for performance, SEO, and modern UI. App Router architecture. |
| **Backend**          | Python (FastAPI)                               | High-performance, async-first framework. Perfect for ML/AI integration.         |
| **Database**         | PostgreSQL with pgvector                       | Robust relational DB + advanced vector search for RAG.                          |
| **AI/ML**            | Google Gemini API                              | State-of-the-art LLM for intelligent content generation.                        |
| **Embeddings**       | Sentence Transformers                          | Open-source model for text→vector conversion.                                   |
| **State Management** | TanStack Query (React Query)                   | Modern server-state management for React.                                       |
| **Styling**          | Tailwind CSS                                   | Utility-first CSS for rapid UI development.                                     |

## 🎯 Key Features

### For Users

- ✅ **Personalized Career Roadmaps** - Input your skills and get custom learning paths
- ✅ **Job Matching** - Find jobs that match your skillset with similarity scores
- ✅ **Skill Gap Analysis** - Identify exactly what you need to learn
- ✅ **Resource Recommendations** - Get curated learning materials for each step
- ✅ **Timeline Estimates** - Realistic timeframes for career transitions
- ✅ **Confidence Scores** - Know how ready you are for your target role

### Technical Highlights

- ✅ **Vector Search** - Semantic similarity using pgvector and cosine distance
- ✅ **RAG Pipeline** - Combines retrieval and generation for context-aware responses
- ✅ **Async Operations** - Fast, non-blocking API with FastAPI
- ✅ **Type Safety** - Full TypeScript on frontend, Pydantic on backend
- ✅ **Modern Architecture** - App Router, Server Components, Edge Runtime ready

## 📂 Project Structure

```
skill-coach/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/        # API endpoints
│   │   │   │   ├── skills.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── roadmap.py
│   │   │   └── schemas.py     # Pydantic models
│   │   ├── core/
│   │   │   └── config.py      # Configuration
│   │   ├── db/
│   │   │   ├── database.py    # DB connection
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   └── init_db.py     # Database seeding
│   │   └── services/
│   │       ├── embedding_service.py  # Vector embeddings
│   │       └── gemini_service.py     # Gemini API
│   ├── main.py                # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                   # Next.js Frontend
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx     # Root layout
    │   │   ├── page.tsx       # Home page
    │   │   └── globals.css    # Global styles
    │   ├── components/
    │   │   ├── ui/            # Reusable UI components
    │   │   └── providers.tsx  # React Query provider
    │   └── lib/
    │       ├── api.ts         # API client
    │       └── utils.ts       # Utilities
    ├── package.json
    └── .env.local
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+** with pgvector extension
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Navigate to backend directory**

```bash
cd backend
```

2. **Create virtual environment**

```bash
python -m venv venv
```

3. **Activate virtual environment**

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/skill_coach
GEMINI_API_KEY=your_actual_api_key_here
REDIS_URL=redis://localhost:6379/0
```

6. **Setup PostgreSQL with pgvector**

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE skill_coach;

-- Connect to the database
\c skill_coach

-- Enable pgvector extension
CREATE EXTENSION vector;
```

7. **Initialize database and seed data**

```bash
python -m app.db.init_db
```

8. **Run the API**

```bash
python main.py
```

API will be available at:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to frontend directory**

```bash
cd frontend
```

2. **Install dependencies**

```bash
npm install
# or
pnpm install
```

3. **Configure environment**

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run the development server**

```bash
npm run dev
# or
pnpm dev
```

Frontend will be available at: http://localhost:3000

## 📖 Usage

### 1. Generate a Career Roadmap

1. Visit http://localhost:3000
2. Add your current skills (e.g., "Python", "JavaScript", "React")
3. Enter your target role (e.g., "Senior AI Engineer")
4. Optionally add target salary and experience
5. Click "Generate Career Roadmap"
6. Review your personalized learning path!

### 2. API Endpoints

#### Skills

```bash
# Search skills using vector similarity
curl -X POST "http://localhost:8000/api/v1/skills/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 10}'

# Get trending skills
curl "http://localhost:8000/api/v1/skills/trending/top?limit=10"
```

#### Jobs

```bash
# Match jobs to your skills
curl -X POST "http://localhost:8000/api/v1/jobs/match" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "limit": 10,
    "min_salary": 120000
  }'
```

#### Roadmap

```bash
# Generate career roadmap
curl -X POST "http://localhost:8000/api/v1/roadmap/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_skills": ["Python", "JavaScript", "React"],
    "target_role": "AI Engineer",
    "target_salary": 180000,
    "experience_years": 3
  }'
```

## 🎨 Screenshots

### Home Page - Input Form

Clean, intuitive interface for entering your career goals.

### Generated Roadmap

Detailed, step-by-step learning path with resources and timelines.

### Skill Gap Analysis

Visual representation of what you need to learn.

## 🧪 Technologies Demonstrated

### Data & AI

- ✅ RAG (Retrieval-Augmented Generation) architecture
- ✅ Vector search with pgvector
- ✅ Semantic similarity using cosine distance
- ✅ Text embeddings with Sentence Transformers
- ✅ LLM integration (Gemini API)
- ✅ Complex data modeling with relationships

### Backend

- ✅ High-performance async API design
- ✅ Type-safe Python with Pydantic
- ✅ Database migrations and seeding
- ✅ Error handling and retries
- ✅ CORS configuration
- ✅ API documentation (Swagger/ReDoc)

### Frontend

- ✅ Next.js 14 App Router
- ✅ Server Components
- ✅ Client Components for interactivity
- ✅ TypeScript for type safety
- ✅ TanStack Query for state management
- ✅ Tailwind CSS for styling
- ✅ Responsive design
- ✅ Loading states and error handling

## 🔮 Future Enhancements

- [ ] User authentication and profiles
- [ ] Save and track multiple roadmaps
- [ ] Progress tracking for learning steps
- [ ] Community-contributed resources
- [ ] Real-time job market data updates
- [ ] Skill endorsements and verification
- [ ] Integration with learning platforms (Coursera, Udemy, etc.)
- [ ] Mobile app (React Native)
- [ ] Email notifications for new opportunities
- [ ] Salary predictions based on skills

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project for your portfolio!

## 👤 Author

Built as a portfolio project to demonstrate:

- Modern full-stack development
- AI/ML integration
- Vector databases and RAG architecture
- Production-ready code practices

## 🙏 Acknowledgments

- **Google Gemini API** for AI-powered content generation
- **pgvector** for vector database capabilities
- **FastAPI** for the amazing Python framework
- **Next.js** team for the best React framework
- **Vercel** for deployment platform

---

⭐ If you found this project helpful, please give it a star!

📧 Questions? Feel free to reach out or open an issue.
