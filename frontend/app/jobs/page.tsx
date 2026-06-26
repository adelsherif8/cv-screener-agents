"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppHeader, PageContainer, MainContent, Card, Button, SectionHeader, LoadingSpinner, ErrorDisplay } from "@/components/shared";

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
  status: string;
  location?: string;
  remote_allowed?: boolean;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  employment_type?: string;
  created_at: string;
  view_count: number;
  application_count: number;
  screening_questions?: string[];
}

export default function JobsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
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
    fetchJobs(token);
  }, [router]);

  const fetchJobs = async (token: string) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/users/me/jobs", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const jobsData = await response.json();
        setJobs(jobsData);
      } else if (response.status === 401) {
        // Token expired
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        router.push("/auth/login");
      } else {
        setError("Failed to fetch jobs");
      }
    } catch (error) {
      console.error("Error fetching jobs:", error);
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    router.push("/auth/login");
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "published":
        return "bg-green-100 text-green-800";
      case "draft":
        return "bg-yellow-100 text-yellow-800";
      case "paused":
        return "bg-gray-100 text-gray-800";
      case "closed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "basic":
        return "bg-blue-100 text-blue-700 border-blue-200";
      case "intermediate":
        return "bg-orange-100 text-orange-700 border-orange-200";
      case "advanced":
        return "bg-red-100 text-red-700 border-red-200";
      case "expert":
        return "bg-purple-100 text-purple-700 border-purple-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const formatSalary = (min?: number, max?: number, currency = "USD") => {
    if (!min && !max) return null;
    if (min && max) return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()}`;
    if (min) return `${currency} ${min.toLocaleString()}+`;
    if (max) return `Up to ${currency} ${max.toLocaleString()}`;
    return null;
  };

  const getJobIcon = (title: string) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('frontend') || titleLower.includes('react') || titleLower.includes('vue') || titleLower.includes('angular')) {
      return 'fas fa-desktop';
    } else if (titleLower.includes('backend') || titleLower.includes('api') || titleLower.includes('server')) {
      return 'fas fa-server';
    } else if (titleLower.includes('fullstack') || titleLower.includes('full-stack')) {
      return 'fas fa-layer-group';
    } else if (titleLower.includes('mobile') || titleLower.includes('ios') || titleLower.includes('android')) {
      return 'fas fa-mobile-alt';
    } else if (titleLower.includes('data') || titleLower.includes('analyst') || titleLower.includes('scientist')) {
      return 'fas fa-chart-bar';
    } else if (titleLower.includes('devops') || titleLower.includes('sre') || titleLower.includes('infrastructure')) {
      return 'fas fa-cogs';
    } else if (titleLower.includes('design') || titleLower.includes('ui') || titleLower.includes('ux')) {
      return 'fas fa-paint-brush';
    } else if (titleLower.includes('test') || titleLower.includes('qa') || titleLower.includes('quality')) {
      return 'fas fa-bug';
    } else if (titleLower.includes('security') || titleLower.includes('cyber')) {
      return 'fas fa-shield-alt';
    } else if (titleLower.includes('machine learning') || titleLower.includes('ai') || titleLower.includes('ml')) {
      return 'fas fa-brain';
    } else {
      return 'fas fa-briefcase';
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading your jobs..." />;
  }

  return (
    <PageContainer>
      <AppHeader 
        title="Job Dashboard" 
        subtitle="Manage and track your job postings"
        user={user}
        onLogout={handleLogout}
      />

      <MainContent>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="mb-2 font-bold text-gray-900 text-3xl">Your Job Postings</h2>
            <p className="text-gray-600">Create, manage, and track your job opportunities</p>
          </div>
          <div className="flex gap-3">
            <Button href="/cvs/analyze" variant="outline" size="lg">
              <i className="mr-2 fas fa-brain"></i>
              Analyze CVs
            </Button>
            <Button href="/jobs/create" size="lg">
              <i className="mr-2 fas fa-plus"></i>
              Create New Job
            </Button>
          </div>
        </div>

        {error && (
          <Card className="bg-red-50 mb-6 border-red-200">
            <div className="flex items-center">
              <i className="mr-3 text-red-600 fas fa-exclamation-circle"></i>
              <p className="font-medium text-red-700">{error}</p>
            </div>
          </Card>
        )}

        {jobs.length === 0 ? (
          <Card className="text-center" padding="xl">
            <div className="flex justify-center items-center bg-gradient-to-r from-purple-100 to-blue-100 mx-auto mb-6 rounded-full w-24 h-24">
              <i className="text-purple-600 text-4xl fas fa-briefcase"></i>
            </div>
            <h3 className="mb-4 font-bold text-gray-900 text-2xl">No job postings yet</h3>
            <p className="mx-auto mb-8 max-w-md text-gray-600">
              Get started by creating your first job posting. Our AI will help you craft the perfect description.
            </p>
            <Button href="/jobs/create" size="lg">
              <i className="mr-2 fas fa-rocket"></i>
              Create Your First Job
            </Button>
          </Card>
        ) : (
          <div className="gap-6 grid lg:grid-cols-2 xl:grid-cols-3">
            {jobs.map((job) => (
              <Card
                key={job.id}
                hover
                className="group"
                padding="md"
              >
                {/* Job Header */}
                <div className="flex items-start space-x-4 mb-4">
                  <div className="flex flex-shrink-0 justify-center items-center bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl w-12 h-12">
                    <i className={`text-white text-lg ${getJobIcon(job.title)}`}></i>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="mb-2 font-bold text-gray-900 group-hover:text-purple-700 text-lg line-clamp-2 transition-colors duration-300">
                      {job.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                          job.status
                        )}`}
                      >
                        <span className="bg-current opacity-75 mr-1 rounded-full w-1.5 h-1.5"></span>
                        {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                      </span>
                      {job.seniority && (
                        <span className="bg-purple-50 px-2 py-1 border border-purple-200 rounded-full font-medium text-purple-700 text-xs">
                          <i className="fa-layer-group mr-1 text-xs fas"></i>
                          {job.seniority}
                        </span>
                      )}
                      {job.employment_type && (
                        <span className="bg-blue-50 px-2 py-1 border border-blue-200 rounded-full font-medium text-blue-700 text-xs">
                          <i className="mr-1 text-xs fas fa-clock"></i>
                          {job.employment_type}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Job Meta Info */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600 text-sm">
                    <i className="mr-2 w-4 text-purple-500 fas fa-calendar-alt"></i>
                    <span>Created {formatDate(job.created_at)}</span>
                  </div>
                  {job.location && (
                    <div className="flex items-center text-gray-600 text-sm">
                      <i className="mr-2 w-4 text-blue-500 fas fa-map-marker-alt"></i>
                      <span>{job.location}</span>
                      {job.remote_allowed && (
                        <span className="bg-green-100 ml-2 px-2 py-0.5 rounded text-green-700 text-xs">
                          <i className="mr-1 text-xs fas fa-home"></i>
                          Remote OK
                        </span>
                      )}
                    </div>
                  )}
                  {formatSalary(job.salary_min, job.salary_max, job.salary_currency) && (
                    <div className="flex items-center text-gray-600 text-sm">
                      <i className="mr-2 w-4 text-green-500 fas fa-dollar-sign"></i>
                      <span>{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</span>
                    </div>
                  )}
                </div>

                {/* Skills Preview */}
                {job.requirements && job.requirements.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center mb-2">
                      <i className="mr-2 text-orange-500 text-sm fas fa-tools"></i>
                      <span className="font-medium text-gray-700 text-sm">Key Skills</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {job.requirements.slice(0, 4).map((requirement, index) => (
                        <span
                          key={index}
                          className={`inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium border ${getLevelColor(requirement.level)}`}
                        >
                          <span className="mr-1">{requirement.skill}</span>
                          <span className="opacity-75 text-xs">({requirement.level})</span>
                        </span>
                      ))}
                      {job.requirements.length > 4 && (
                        <span className="bg-gray-100 px-2 py-1 rounded-lg font-medium text-gray-600 text-xs">
                          +{job.requirements.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Job Description Preview */}
                {job.description && (
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm line-clamp-2">
                      {job.description}
                    </p>
                  </div>
                )}

                {/* Job Stats */}
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 mb-4 p-3 rounded-xl">
                  <div className="gap-4 grid grid-cols-2">
                    <div className="text-center">
                      <div className="flex justify-center items-center bg-white shadow-sm mb-2 rounded-lg w-8 h-8">
                        <i className="text-purple-600 text-sm fas fa-eye"></i>
                      </div>
                      <div className="font-bold text-gray-900 text-sm">{job.view_count}</div>
                      <div className="text-gray-600 text-xs">Views</div>
                    </div>
                    <div className="text-center">
                      <div className="flex justify-center items-center bg-white shadow-sm mb-2 rounded-lg w-8 h-8">
                        <i className="text-blue-600 text-sm fas fa-users"></i>
                      </div>
                      <div className="font-bold text-gray-900 text-sm">{job.application_count}</div>
                      <div className="text-gray-600 text-xs">Applications</div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <Button href={`/jobs/${job.id}`} size="sm" className="flex-1">
                    <i className="mr-2 fas fa-eye"></i>
                    View Details
                  </Button>
                  <Button 
                    href={`/jobs/${job.id}/analyze-cvs`} 
                    variant="primary" 
                    size="sm"
                    className="flex-1"
                  >
                    <i className="mr-2 fas fa-file-search"></i>
                    Analyze CVs
                  </Button>
                  <Button 
                    href={`/jobs/${job.id}/edit`} 
                    variant="secondary" 
                    size="sm"
                    className="px-3"
                  >
                    <i className="fas fa-edit"></i>
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </MainContent>
    </PageContainer>
  );
}
