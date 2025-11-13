"use client";
"use client";

import { useState } from "react";

import { useMutation } from "@tanstack/react-query";

import {
  roadmapApi,
  type RoadmapRequest,
  type RoadmapResponse,
} from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

import { Loader2, Sparkles, TrendingUp, Target, Clock } from "lucide-react";
import { request } from "https";

export default function Home() {
  const [currentSkills, setCurrentSkills] = useState<string[]>([]);

  const [skillInput, setSkillInput] = useState("");

  const [targetRole, setTargetRole] = useState("");

  const [targetSalary, setTargetSalary] = useState("");

  const [experienceYears, setExperienceYears] = useState("");

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const generateRoadmapMutation = useMutation<
    RoadmapResponse,
    Error,
    RoadmapRequest
  >({
    mutationFn: (data: RoadmapRequest) => roadmapApi.generate(data),
    onSuccess: (data) => {
      setRoadmap(data);
      setErrorMessage(null);
    },
    onError: (error: any) => {
      // Extract user-friendly error message from API response
      const message =
        error.response?.data?.detail ||
        error.message ||
        "An unexpected error occurred";
      setErrorMessage(message);
    },
  });

  const addSkill = () => {
    const trimmed = skillInput.trim();
    if (trimmed && !currentSkills.includes(trimmed)) {
      setCurrentSkills([...currentSkills, trimmed]);
      setSkillInput("");
    }
  };

  const removeSkill = (skill: string) => {
    setCurrentSkills(currentSkills.filter((s) => s !== skill));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (currentSkills.length === 0 || !targetRole.trim()) {
      alert("Please add at least one skill and specify a target role");
      return;
    }

    const request: RoadmapRequest = {
      current_skills: currentSkills,
      target_role: targetRole.trim(),
      target_salary: targetSalary ? parseFloat(targetSalary) : undefined,
      experience_years: experienceYears
        ? parseFloat(experienceYears)
        : undefined,
    };

    generateRoadmapMutation.mutate(request);
  };

  return (
    <div className="min-h-screen bg-gradient-to from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-3">
            <Sparkles className="text-blue-600" size={48} />
            Skill Coach
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Career Path Navigator
          </p>

          <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
            <h2 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
              Get personalized learning roadmaps powered by RAG and Vector
              Search
            </h2>
            <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
              To get started, edit the page.tsx file. Looking for a starting
              point or more instructions? Head over to the resources below.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="text-blue-600" />
                Your Career Goals
              </CardTitle>
              <CardDescription>
                Tell us about your current skills and where you want to go
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Current Skills */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Current Skills *
                  </label>
                  <div className="flex gap-2 mb-3">
                    <Input
                      placeholder="e.g., Python, JavaScript, React"
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      onKeyPress={(e) =>
                        e.key === "Enter" && (e.preventDefault(), addSkill())
                      }
                    />
                    <Button type="button" onClick={addSkill} variant="outline">
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {currentSkills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2"
                      >
                        {skill}
                        <button
                          type="button"
                          onClick={() => removeSkill(skill)}
                          className="hover:text-blue-900"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Target Role */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Target Role *
                  </label>
                  <Input
                    placeholder="e.g., Senior AI Engineer, Full Stack Developer"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    required
                  />
                </div>

                {/* Target Salary */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Target Salary (USD/year)
                  </label>
                  <Input
                    type="number"
                    placeholder="e.g., 150000"
                    value={targetSalary}
                    onChange={(e) => setTargetSalary(e.target.value)}
                  />
                </div>

                {/* Experience Years */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Years of Experience
                  </label>
                  <Input
                    type="number"
                    step="0.5"
                    placeholder="e.g., 3"
                    value={experienceYears}
                    onChange={(e) => setExperienceYears(e.target.value)}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
                  disabled={generateRoadmapMutation.isPending}
                >
                  {generateRoadmapMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 animate-spin" size={20} />
                      Generating Your Roadmap...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2" size={20} />
                      Generate Career Roadmap
                    </>
                  )}
                </Button>

                {errorMessage && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800 font-medium mb-1">
                      Unable to Generate Roadmap
                    </p>
                    <p className="text-red-600 text-sm">{errorMessage}</p>
                  </div>
                )}
              </form>
            </CardContent>
          </Card>

          {/* Right column: loading state or roadmap */}
          <div>
            {generateRoadmapMutation.isPending && (
              <div className="text-center">
                <Loader2
                  className="mx-auto animate-spin text-blue-600 mb-4"
                  size={48}
                />
                <p className="text-gray-600">
                  Analyzing job market data and generating your personalized
                  roadmap...
                </p>
              </div>
            )}

            {roadmap && (
              <>
                {/* Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="text-green-600" />
                      Career Roadmap: {roadmap.target_role}
                    </CardTitle>
                    <CardDescription>
                      Generated on{" "}
                      {new Date(roadmap.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">
                          Confidence Score
                        </p>
                        <p className="text-2xl font-bold text-blue-600">
                          {(roadmap.confidence_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                          <Clock size={14} />
                          Timeline
                        </p>
                        <p className="text-2xl font-bold text-purple-600">
                          {roadmap.estimated_timeline}
                        </p>
                      </div>
                    </div>

                    {/* Skill Gaps */}
                    <div>
                      <h4 className="font-semibold mb-2">Skills to Learn</h4>
                      <div className="flex flex-wrap gap-2">
                        {roadmap.skill_gaps.map((skill) => (
                          <span
                            key={skill}
                            className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Recommended Skills */}
                    {roadmap.recommended_skills.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Bonus Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {roadmap.recommended_skills
                            .slice(0, 5)
                            .map((skill) => (
                              <span
                                key={skill}
                                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                              >
                                {skill}
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Learning Path */}
                {roadmap.learning_path.map((step) => (
                  <Card key={step.step}>
                    <CardHeader>
                      <div className="flex items-start gap-3">
                        <div className="bg-blue-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shrink-0">
                          {step.step}
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-lg">
                            {step.title}
                          </CardTitle>
                          <CardDescription className="flex items-center gap-2 mt-1">
                            <Clock size={14} />
                            {step.estimated_duration}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-gray-700">{step.description}</p>

                      {step.resources.length > 0 && (
                        <div>
                          <h5 className="font-semibold mb-2 text-sm">
                            Resources
                          </h5>
                          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                            {step.resources.map((resource, idx) => (
                              <li key={idx}>{resource}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {step.skills_gained.length > 0 && (
                        <div>
                          <h5 className="font-semibold mb-2 text-sm">
                            Skills Gained
                          </h5>
                          <div className="flex flex-wrap gap-2">
                            {step.skills_gained.map((skill) => (
                              <span
                                key={skill}
                                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
