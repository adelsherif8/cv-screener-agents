"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { 
  AppHeader, PageContainer, MainContent, Card, Button, SectionHeader, LoadingSpinner, ErrorDisplay 
} from "@/components/shared";

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  company_name?: string;
  job_title?: string;
}

interface Job {
  id: number;
  title: string;
  description: string;
  requirements: Array<{
    skill: string;
    level: string;
    weight: string;
  }>;
  seniority?: string;
  summary?: string;
  location?: string;
  remote_allowed: boolean;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  employment_type?: string;
  status: string;
  screening_questions: string[];
}

export default function JobEditPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.id as string;
  
  const [user, setUser] = useState<User | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (!token || !userData) {
      router.push("/auth/login");
      return;
    }

    setUser(JSON.parse(userData));
    fetchJob(token, jobId);
  }, [router, jobId]);

  const fetchJob = async (token: string, id: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/users/me/jobs/${id}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const jobData = await response.json();
        setJob(jobData);
      } else if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        router.push("/auth/login");
      } else if (response.status === 404) {
        setError("Job not found");
      } else {
        setError("Failed to fetch job details");
      }
    } catch (error) {
      console.error("Error fetching job:", error);
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!job) return;
    
    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`http://127.0.0.1:8000/users/me/jobs/${jobId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(job),
      });

      if (response.ok) {
        router.push(`/jobs/${jobId}`);
      } else {
        setError("Failed to save job");
      }
    } catch (error) {
      console.error("Error saving job:", error);
      setError("Network error");
    } finally {
      setSaving(false);
    }
  };

  const addRequirement = () => {
    if (!job) return;
    setJob({
      ...job,
      requirements: [...job.requirements, { skill: "", level: "Basic", weight: "0.5" }]
    });
  };

  const removeRequirement = (index: number) => {
    if (!job) return;
    setJob({
      ...job,
      requirements: job.requirements.filter((_, i) => i !== index)
    });
  };

  const updateRequirement = (index: number, field: string, value: string) => {
    if (!job) return;
    const updatedRequirements = [...job.requirements];
    updatedRequirements[index] = { ...updatedRequirements[index], [field]: value };
    setJob({ ...job, requirements: updatedRequirements });
  };

  const addScreeningQuestion = () => {
    if (!job) return;
    setJob({
      ...job,
      screening_questions: [...job.screening_questions, ""]
    });
  };

  const removeScreeningQuestion = (index: number) => {
    if (!job) return;
    setJob({
      ...job,
      screening_questions: job.screening_questions.filter((_, i) => i !== index)
    });
  };

  const updateScreeningQuestion = (index: number, value: string) => {
    if (!job) return;
    const updatedQuestions = [...job.screening_questions];
    updatedQuestions[index] = value;
    setJob({ ...job, screening_questions: updatedQuestions });
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    router.push("/auth/login");
  };

  if (loading) {
    return (
      <PageContainer>
        <div className="flex justify-center items-center min-h-[50vh]">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="flex justify-center items-center min-h-[50vh]">
          <ErrorDisplay 
            message={error}
            actions={
              <Button href="/jobs">
                <i className="fa-arrow-left mr-2 fas"></i>
                Back to Jobs
              </Button>
            }
          />
        </div>
      </PageContainer>
    );
  }

  if (!job) {
    return null;
  }

  return (
    <PageContainer>
      <AppHeader 
        title={`Edit: ${job.title}`}
        subtitle={`Job #${job.id} • Edit job details and requirements`}
        backHref={`/jobs/${job.id}`}
        backLabel="Back to Job"
        actions={
          <div className="flex space-x-3">
            <Button
              onClick={handleSave}
              disabled={saving}
              variant="primary"
            >
              {saving ? (
                <>
                  <i className="mr-2 fas fa-spinner fa-spin"></i>
                  Saving...
                </>
              ) : (
                <>
                  <i className="mr-2 fas fa-save"></i>
                  Save Changes
                </>
              )}
            </Button>
          </div>
        }
      />

      <MainContent>
        <div className="space-y-6 mx-auto max-w-4xl">
          {/* Basic Information */}
          <Card padding="lg">
            <SectionHeader 
              title="Basic Information" 
              icon="fas fa-info-circle"
            />
            <div className="gap-6 grid md:grid-cols-2">
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Job Title</label>
                <input
                  type="text"
                  value={job.title}
                  onChange={(e) => setJob({ ...job, title: e.target.value })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                />
              </div>
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Seniority Level</label>
                <select
                  value={job.seniority || ""}
                  onChange={(e) => setJob({ ...job, seniority: e.target.value })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                >
                  <option value="">Select Seniority</option>
                  <option value="Junior">Junior</option>
                  <option value="Mid-level">Mid-level</option>
                  <option value="Senior">Senior</option>
                  <option value="Lead">Lead</option>
                  <option value="Principal">Principal</option>
                </select>
              </div>
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Location</label>
                <input
                  type="text"
                  value={job.location || ""}
                  onChange={(e) => setJob({ ...job, location: e.target.value })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                />
              </div>
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Employment Type</label>
                <select
                  value={job.employment_type || ""}
                  onChange={(e) => setJob({ ...job, employment_type: e.target.value })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                >
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
            </div>
            <div className="mt-6">
              <label className="block mb-2 font-semibold text-gray-700">Job Description</label>
              <textarea
                value={job.description}
                onChange={(e) => setJob({ ...job, description: e.target.value })}
                rows={8}
                className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
              />
            </div>
          </Card>

          {/* Salary Information */}
          <Card padding="lg">
            <SectionHeader 
              title="Salary Information" 
              icon="fas fa-dollar-sign"
            />
            <div className="gap-6 grid md:grid-cols-3">
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Minimum Salary</label>
                <input
                  type="number"
                  value={job.salary_min || ""}
                  onChange={(e) => setJob({ ...job, salary_min: parseInt(e.target.value) || undefined })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                />
              </div>
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Maximum Salary</label>
                <input
                  type="number"
                  value={job.salary_max || ""}
                  onChange={(e) => setJob({ ...job, salary_max: parseInt(e.target.value) || undefined })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                />
              </div>
              <div>
                <label className="block mb-2 font-semibold text-gray-700">Currency</label>
                <select
                  value={job.salary_currency || "USD"}
                  onChange={(e) => setJob({ ...job, salary_currency: e.target.value })}
                  className="bg-white px-4 py-3 border border-gray-300 focus:border-purple-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-200 w-full transition-all duration-300"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="CAD">CAD (C$)</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Requirements */}
          <Card padding="lg">
            <div className="flex justify-between items-center mb-6">
              <SectionHeader 
                title="Skills & Requirements" 
                icon="fas fa-cogs"
              />
              <Button
                onClick={addRequirement}
                variant="primary"
                size="sm"
              >
                <i className="mr-2 fas fa-plus"></i>
                Add Skill
              </Button>
            </div>
            <div className="space-y-4">
              {job.requirements.map((requirement, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-xl">
                  <div className="gap-4 grid md:grid-cols-4">
                    <div className="md:col-span-2">
                      <label className="block mb-1 font-medium text-gray-700 text-sm">Skill</label>
                      <input
                        type="text"
                        value={requirement.skill}
                        onChange={(e) => updateRequirement(index, "skill", e.target.value)}
                        className="bg-white px-3 py-2 border border-gray-300 focus:border-blue-500 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-200 w-full transition-all duration-300"
                        placeholder="e.g., React, Python, JavaScript"
                      />
                    </div>
                    <div>
                      <label className="block mb-1 font-medium text-gray-700 text-sm">Level</label>
                      <select
                        value={requirement.level}
                        onChange={(e) => updateRequirement(index, "level", e.target.value)}
                        className="bg-white px-3 py-2 border border-gray-300 focus:border-blue-500 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-200 w-full transition-all duration-300"
                      >
                        <option value="Basic">Basic</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                        <option value="Expert">Expert</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <button
                        onClick={() => removeRequirement(index)}
                        className="bg-red-100 hover:bg-red-200 p-2 rounded-lg text-red-600 transition-colors duration-300"
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Screening Questions */}
          <Card padding="lg">
            <div className="flex justify-between items-center mb-6">
              <SectionHeader 
                title="Screening Questions" 
                icon="fas fa-question-circle"
              />
              <Button
                onClick={addScreeningQuestion}
                variant="primary"
                size="sm"
              >
                <i className="mr-2 fas fa-plus"></i>
                Add Question
              </Button>
            </div>
            <div className="space-y-4">
              {job.screening_questions.map((question, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-xl">
                  <div className="flex space-x-4">
                    <div className="flex-1">
                      <textarea
                        value={question}
                        onChange={(e) => updateScreeningQuestion(index, e.target.value)}
                        className="bg-white px-3 py-2 border border-gray-300 focus:border-orange-500 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-200 w-full transition-all duration-300"
                        placeholder="Enter your screening question..."
                        rows={2}
                      />
                    </div>
                    <button
                      onClick={() => removeScreeningQuestion(index)}
                      className="bg-red-100 hover:bg-red-200 p-2 rounded-lg text-red-600 transition-colors duration-300"
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Actions */}
          <Card padding="lg">
            <div className="flex justify-between items-center">
              <Button
                href={`/jobs/${jobId}`}
                variant="secondary"
              >
                <i className="mr-2 fas fa-times"></i>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving}
                variant="primary"
              >
                {saving ? (
                  <>
                    <i className="mr-2 fas fa-spinner fa-spin"></i>
                    Saving Changes...
                  </>
                ) : (
                  <>
                    <i className="mr-2 fas fa-save"></i>
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>
      </MainContent>
    </PageContainer>
  );
}
