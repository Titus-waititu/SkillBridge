import axios from "axios";
import dotenv from 'dotenv';

dotenv.config();

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Skill {
  id: number;
  name: string;
  category: string;
  demand_score?: number;
  avg_salary_impact?: number;
  created_at: string;
}

export interface JobPosting {
  id: number;
  title: string;
  company?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  description?: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_level?: string;
  remote_type?: string;
  created_at: string;
}

export interface JobMatchResult {
  job_id: number;
  title: string;
  company?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  required_skills: string[];
  match_score: number;
  missing_skills: string[];
}

export interface LearningStep {
  step: number;
  title: string;
  description: string;
  estimated_duration: string;
  resources: string[];
  skills_gained: string[];
}

export interface RoadmapResponse {
  id: number;
  target_role: string;
  current_skills: string[];
  skill_gaps: string[];
  recommended_skills: string[];
  learning_path: LearningStep[];
  estimated_timeline: string;
  confidence_score: number;
  created_at: string;
}

export interface RoadmapRequest {
  current_skills: string[];
  target_role: string;
  target_salary?: number;
  experience_years?: number;
}

// API Functions
export const skillsApi = {
  list: async (category?: string) => {
    const params = category ? { category } : {};
    const response = await api.get<Skill[]>("/skills/", { params });
    return response.data;
  },

  trending: async (limit: number = 10) => {
    const response = await api.get<Skill[]>("/skills/trending/top", {
      params: { limit },
    });
    return response.data;
  },

  search: async (query: string, limit: number = 10) => {
    const response = await api.post("/skills/search", { query, limit });
    return response.data;
  },
};

export const jobsApi = {
  list: async (filters?: {
    skip?: number;
    limit?: number;
    experience_level?: string;
    remote_type?: string;
  }) => {
    const response = await api.get<JobPosting[]>("/jobs/", { params: filters });
    return response.data;
  },

  match: async (data: {
    skills: string[];
    limit?: number;
    min_salary?: number;
    experience_level?: string;
    remote_type?: string;
  }) => {
    const response = await api.post<JobMatchResult[]>("/jobs/match", data);
    return response.data;
  },

  stats: async () => {
    const response = await api.get("/jobs/stats/summary");
    return response.data;
  },
};

export const roadmapApi = {
  generate: async (data: RoadmapRequest) => {
    const response = await api.post<RoadmapResponse>("/roadmap/generate", data);
    return response.data;
  },

  get: async (id: number) => {
    const response = await api.get<RoadmapResponse>(`/roadmap/${id}`);
    return response.data;
  },
};
