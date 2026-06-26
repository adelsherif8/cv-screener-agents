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
  created_at: string;
  updated_at: string;
  published_at?: string;
  view_count: number;
  application_count: number;
  screening_questions: string[];
  domain_tags: string[];
  ats_keywords: string[];
  user: User;
}

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.id as string;
  
  const [user, setUser] = useState<User | null>(null);
  const [job, setJob] = useState<Job | null>(null);
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

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    router.push("/auth/login");
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "published":
        return "bg-green-100 text-green-800 border-green-200";
      case "draft":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "paused":
        return "bg-gray-100 text-gray-800 border-gray-200";
      case "closed":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "basic":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "intermediate":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "advanced":
        return "bg-red-100 text-red-800 border-red-200";
      case "expert":
        return "bg-purple-100 text-purple-800 border-purple-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const formatSalary = (min?: number, max?: number, currency = "USD") => {
    if (!min && !max) return "Salary not specified";
    if (min && max) return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()}`;
    if (min) return `${currency} ${min.toLocaleString()}+`;
    if (max) return `Up to ${currency} ${max.toLocaleString()}`;
    return "Salary not specified";
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
        title={job.title}
        subtitle={`Job #${job.id} • Created ${formatDate(job.created_at)}`}
        backHref="/jobs"
        backLabel="Back to Jobs"
        actions={
          <div className="flex space-x-3">
            <Button href={`/jobs/${job.id}/analyze-cvs`} variant="primary">
              <i className="mr-2 fas fa-file-search"></i>
              Analyze CVs
            </Button>
            <Button href={`/jobs/${job.id}/edit`} variant="secondary">
              <i className="mr-2 fas fa-edit"></i>
              Edit Job
            </Button>
          </div>
        }
      />

      <MainContent>
        <div className="gap-8 grid lg:grid-cols-3">
          {/* Job Details - Main Column */}
          <div className="space-y-6 lg:col-span-2">
            {/* Job Header */}
            <Card padding="lg">
              <div className="flex justify-between items-start mb-6">
                <div className="flex-1">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="flex justify-center items-center bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl w-16 h-16">
                      <i className="text-white text-2xl fas fa-briefcase"></i>
                    </div>
                    <div>
                      <h1 className="font-bold text-gray-900 text-3xl">{job.title}</h1>
                      <p className="text-gray-600 text-lg">{job.user.company_name || "Company"}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-4">
                    <span className={`px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(job.status)}`}>
                      <i className="inline-block bg-current mr-2 rounded-full w-2 h-2"></i>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                    {job.employment_type && (
                      <span className="bg-blue-50 px-4 py-2 border border-blue-200 rounded-full font-medium text-blue-800 text-sm">
                        {job.employment_type.charAt(0).toUpperCase() + job.employment_type.slice(1)}
                      </span>
                    )}
                    {job.seniority && (
                      <span className="bg-purple-50 px-4 py-2 border border-purple-200 rounded-full font-medium text-purple-800 text-sm">
                        {job.seniority}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex space-x-3">
                  <Link
                    href={`/jobs/${job.id}/edit`}
                    className="bg-blue-100 hover:bg-blue-200 px-6 py-3 rounded-xl font-semibold text-blue-700 transition-all duration-300"
                  >
                    <i className="mr-2 fas fa-edit"></i>
                    Edit Job
                  </Link>
                </div>
              </div>

              {/* Job Meta */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-2xl">
                <div className="gap-6 grid md:grid-cols-2 lg:grid-cols-4">
                  <div className="text-center">
                    <i className="mb-2 text-purple-600 text-2xl fas fa-map-marker-alt"></i>
                    <div className="font-semibold text-gray-900">{job.location || "Remote"}</div>
                    <div className="text-gray-600 text-sm">Location</div>
                  </div>
                  <div className="text-center">
                    <i className="mb-2 text-blue-600 text-2xl fas fa-dollar-sign"></i>
                    <div className="font-semibold text-gray-900">{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</div>
                    <div className="text-gray-600 text-sm">Salary</div>
                  </div>
                  <div className="text-center">
                    <i className="mb-2 text-green-600 text-2xl fas fa-eye"></i>
                    <div className="font-semibold text-gray-900">{job.view_count}</div>
                    <div className="text-gray-600 text-sm">Views</div>
                  </div>
                  <div className="text-center">
                    <i className="mb-2 text-orange-600 text-2xl fas fa-users"></i>
                    <div className="font-semibold text-gray-900">{job.application_count}</div>
                    <div className="text-gray-600 text-sm">Applications</div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Job Summary */}
            {job.summary && (
              <Card padding="lg">
                <SectionHeader 
                  title="Job Summary" 
                  icon="fas fa-clipboard-list"
                />
                <div className="max-w-none prose prose-lg">
                  <div 
                    className="text-gray-700 leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: job.summary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }}
                  />
                </div>
              </Card>
            )}

            {/* Job Description */}
            <Card padding="lg">
              <SectionHeader 
                title="Job Description" 
                icon="fas fa-file-alt"
              />
              <div className="max-w-none prose prose-lg">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{job.description}</p>
              </div>
            </Card>

            {/* Requirements */}
            {job.requirements && job.requirements.length > 0 && (
              <Card padding="lg">
                <SectionHeader 
                  title="Requirements & Skills" 
                  icon="fas fa-check-circle"
                />
                <div className="gap-3 grid sm:grid-cols-2 lg:grid-cols-3">
                  {job.requirements.map((requirement, index) => (
                    <div
                      key={index}
                      className="bg-gradient-to-r from-gray-50 to-white p-4 border border-gray-200 hover:border-purple-300 rounded-xl hover:scale-105 transition-all duration-300 transform"
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{requirement.skill}</h3>
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium mt-2 border ${getLevelColor(requirement.level)}`}>
                            {requirement.level}
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="text-gray-500 text-xs">Weight</div>
                          <div className="font-bold text-purple-600">{Math.round(parseFloat(requirement.weight) * 100)}%</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Screening Questions */}
            {job.screening_questions && job.screening_questions.length > 0 && (
              <Card padding="lg">
                <SectionHeader 
                  title="Screening Questions" 
                  icon="fas fa-question-circle"
                />
                <div className="space-y-4">
                  {job.screening_questions.map((question, index) => (
                    <div
                      key={index}
                      className="bg-gradient-to-r from-orange-50 to-yellow-50 p-4 border border-orange-200 rounded-xl"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex justify-center items-center bg-orange-200 rounded-full w-8 h-8 font-bold text-orange-800 text-sm">
                          {index + 1}
                        </div>
                        <p className="flex-1 text-gray-700">{question}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card padding="md">
              <SectionHeader 
                title="Quick Actions" 
                icon="fas fa-tools"
                size="sm"
              />
              <div className="space-y-3">
                <Link
                  href={`/jobs/${job.id}/edit`}
                  className="flex items-center bg-gradient-to-r from-blue-600 hover:from-blue-700 to-blue-700 hover:to-blue-800 p-3 rounded-xl w-full font-semibold text-white transition-all duration-300"
                >
                  <i className="mr-3 fas fa-edit"></i>
                  Edit Job
                </Link>
                <button className="flex items-center bg-gradient-to-r from-green-600 hover:from-green-700 to-green-700 hover:to-green-800 p-3 rounded-xl w-full font-semibold text-white transition-all duration-300">
                  <i className="mr-3 fas fa-share"></i>
                  Share Job
                </button>
                <button className="flex items-center bg-gradient-to-r from-orange-600 hover:from-orange-700 to-orange-700 hover:to-orange-800 p-3 rounded-xl w-full font-semibold text-white transition-all duration-300">
                  <i className="mr-3 fas fa-pause"></i>
                  {job.status === 'published' ? 'Pause' : 'Publish'} Job
                </button>
              </div>
            </Card>

            {/* Job Timeline */}
            <Card padding="md">
              <SectionHeader 
                title="Timeline" 
                icon="fas fa-clock"
                size="sm"
              />
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <i className="text-blue-600 fas fa-plus"></i>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">Job Created</p>
                    <p className="text-gray-600 text-xs">{formatDate(job.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="bg-green-100 p-2 rounded-lg">
                    <i className="text-green-600 fas fa-edit"></i>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">Last Updated</p>
                    <p className="text-gray-600 text-xs">{formatDate(job.updated_at)}</p>
                  </div>
                </div>
                {job.published_at && (
                  <div className="flex items-start space-x-3">
                    <div className="bg-purple-100 p-2 rounded-lg">
                      <i className="text-purple-600 fas fa-rocket"></i>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 text-sm">Published</p>
                      <p className="text-gray-600 text-xs">{formatDate(job.published_at)}</p>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            {/* Tags */}
            {job.domain_tags && job.domain_tags.length > 0 && (
              <Card padding="md">
                <SectionHeader 
                  title="Tags" 
                  icon="fas fa-tags"
                  size="sm"
                />
                <div className="flex flex-wrap gap-2">
                  {job.domain_tags.map((tag, index) => (
                    <span
                      key={index}
                      className="bg-gradient-to-r from-green-100 to-blue-100 px-3 py-1 border border-green-200 rounded-full text-green-800 text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </MainContent>
    </PageContainer>
  );
}
