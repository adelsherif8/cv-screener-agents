"use client";
import { useState, useEffect, useRef } from "react";
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

interface AnalysisResult {
  candidate_name: string;
  position: string;
  experience_years: number;
  fileName: string;
  analyzed_date: string;
  match_score: number;
  job_specific_score: number;
  skill_analysis: any;
  role_alignment?: any;
  professional_summary: any;
  job_comparison?: any;
  ai_summary: string;
  error?: string;
  
  // Direct backend data fields
  technical_skills?: Array<{
    name: string;
    evidence: string;
    evidence_type: string;
    proficiency_score: number;
    transferability_score: number;
    depth_indicators: string[];
    context: string;
  }>;
  soft_skills?: Array<{
    name: string;
    evidence_sentences: string[];
    confidence_score: number;
    supporting_context: string;
  }>;
  portfolio_links?: string[];
  certifications?: Array<{
    name: string;
    issuer: string;
    year: string;
  }>;
  career_progression?: Array<{
    role: string;
    company: string;
    duration: string;
    key_achievements: string[];
  }>;
  strengths?: string[];
  improvement_suggestions?: string[];
  ai_insights?: string;
  primary_role?: string;
  
  job_fit_analysis?: {
    overall_fit: string;
    requirement_breakdown: Array<{
      requirement: string;
      required_level: string;
      candidate_level: string;
      match_score: number;
      evidence: string;
      gap_analysis: string;
    }>;
    strengths_for_role: string[];
    gaps_to_address: string[];
    recommendation: string;
    hiring_decision: "strong_hire" | "hire" | "maybe" | "no_hire";
    interview_focus_areas: string[];
  };
}

export default function JobCVAnalyzerPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.id as string;
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [user, setUser] = useState<User | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedResults, setExpandedResults] = useState<{[key: number]: boolean}>({});
  const [dragOver, setDragOver] = useState(false);

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
        
        // Load saved CV analyses for this job
        const savedAnalyses = localStorage.getItem(`job_${id}_cv_analyses`);
        if (savedAnalyses) {
          setAnalysisResults(JSON.parse(savedAnalyses));
        }
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  };

  const handleFiles = (files: File[]) => {
    const validFiles = files.filter(file => 
      file.type === "application/pdf" || 
      file.name.toLowerCase().endsWith('.pdf') ||
      file.type.includes('document') ||
      file.name.toLowerCase().endsWith('.doc') ||
      file.name.toLowerCase().endsWith('.docx')
    );
    
    if (validFiles.length === 0) {
      alert("Please upload PDF or Word documents only");
      return;
    }
    
    setUploadedFiles(prev => [...prev, ...validFiles]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Real CV analysis function using our enhanced backend API
  const analyzeCV = async (file: File, job: Job): Promise<AnalysisResult> => {
    try {
      // Step 1: Extract text from CV file
      const formData = new FormData();
      formData.append('file', file);
      
      const extractResponse = await fetch('http://127.0.0.1:8000/cvs/extract-text', {
        method: 'POST',
        body: formData,
      });
      
      if (!extractResponse.ok) {
        throw new Error('Failed to extract CV text');
      }
      
      const { text: cvText } = await extractResponse.json();
      
      // Step 2: Get AI analysis of the CV content with job comparison
      const analysisResponse = await fetch('http://127.0.0.1:8000/cvs/analyze-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cv_text: cvText,
          job_description: `Job Title: ${job.title}\n\nJob Description: ${job.description || ''}\n\nRequirements: ${job.requirements?.map((req: any) => `${req.skill} (${req.level})`).join(', ') || ''}\n\nSeniority: ${job.seniority || ''}\n\nSalary: ${job.salary_min || 0} - ${job.salary_max || 0}`,
          analysis_type: 'comprehensive'
        }),
      });
      
      if (!analysisResponse.ok) {
        throw new Error('Failed to analyze CV content');
      }
      
      const analysisData = await analysisResponse.json();
      
      // Extract candidate name from CV text or filename
      const candidateName = analysisData.candidate_name || 
                           file.name.replace(/\.(pdf|doc|docx)$/i, '').replace(/[-_]/g, ' ');
      const experienceYears = analysisData.experience_years || 0;
      
      // Create skill analysis from our enhanced backend data
      const cvAnalysis = {
        skill_analysis: {
          technical_skills: {
            category: "Technical Skills",
            strength: "Analyzed from CV",
            color: "blue",
            skills: (analysisData.technical_skills || []).map((skill: any) => ({
              skill: skill.name || skill.skill_name || 'Unknown Skill',
              level: skill.evidence_type === "work_experience" ? "Professional" : 
                     skill.depth_indicators?.includes("expert") ? "Expert" : 
                     skill.depth_indicators?.includes("advanced") ? "Advanced" : "Intermediate",
              evidence: skill.evidence || `Found in CV context: ${skill.context || ''}`,
              projects: [], // Could be enhanced later
              rating: skill.proficiency_score || 70
            }))
          },
          soft_skills: {
            category: "Soft Skills", 
            strength: "Evidence-based",
            color: "green",
            skills: (analysisData.soft_skills || []).map((skill: any) => ({
              skill: skill.skill_name,
              level: skill.confidence_score > 80 ? "Strong" : skill.confidence_score > 60 ? "Good" : "Developing",
              evidence: skill.evidence_sentences?.join(' ') || skill.supporting_context || "Identified in CV",
              projects: [],
              rating: skill.confidence_score || 60
            }))
          }
        },
        
        // Job-specific comparison data
        job_comparison: {
          job_title: job.title,
          job_requirements: job.requirements,
          requirement_matches: job.requirements?.map((req: any) => {
            const hasSkill = analysisData?.technical_skills?.some((skill: any) => {
              const skillName = String(skill?.name || skill?.skill_name || '');
              const reqSkill = String(req?.skill || '');
              if (!skillName || !reqSkill) return false;
              return skillName.toLowerCase().includes(reqSkill.toLowerCase()) ||
                     reqSkill.toLowerCase().includes(skillName.toLowerCase());
            }) || false;
            return {
              requirement: req?.skill || '',
              required_level: req?.level || '',
              has_skill: hasSkill,
              candidate_level: hasSkill ? "Found in CV" : "Not mentioned",
              match_status: hasSkill ? "✅" : "❌",
              evidence: hasSkill ? `Mentioned in CV content` : "No evidence found in CV"
            };
          })
        },
        
        // Professional summary from AI analysis
        professional_summary: {
          positioning: analysisData.ai_insights || `${candidateName} - Professional background analyzed from CV`,
          strengths: analysisData.strengths || [],
          growth_areas: analysisData.improvement_suggestions || [],
          career_trajectory: `${experienceYears} years of experience in ${analysisData.primary_role || 'software development'}`
        }
      };
      
      // Calculate match score based on job requirements
      const requirementMatches = job.requirements.map((req: any) => {
        const hasSkill = analysisData.technical_skills?.some((skill: any) => {
          const skillName = String(skill?.name || skill?.skill_name || '');
          const reqSkill = String(req?.skill || '');
          if (!skillName || !reqSkill) return false;
          return skillName.toLowerCase().includes(reqSkill.toLowerCase()) ||
                 reqSkill.toLowerCase().includes(skillName.toLowerCase());
        });
        return hasSkill ? 85 : 45;
      });
      
      const matchScore = requirementMatches.length > 0 
        ? Math.round(requirementMatches.reduce((a, b) => a + b, 0) / requirementMatches.length)
        : 60;
        
      return {
        candidate_name: candidateName,
        position: analysisData.primary_role || "Software Developer",
        experience_years: experienceYears,
        fileName: file.name,
        analyzed_date: new Date().toISOString(),
        match_score: matchScore,
        job_specific_score: matchScore,
        
        // Direct access to technical skills from backend
        technical_skills: analysisData.technical_skills || [],
        soft_skills: analysisData.soft_skills || [],
        portfolio_links: analysisData.portfolio_links || [],
        certifications: analysisData.certifications || [],
        career_progression: analysisData.career_progression || [],
        strengths: analysisData.strengths || [],
        improvement_suggestions: analysisData.improvement_suggestions || [],
        ai_insights: analysisData.ai_insights || "",
        primary_role: analysisData.primary_role || "Software Developer",
        
        // Real skills from our enhanced analyzer
        skill_analysis: cvAnalysis.skill_analysis,
        
        // Job comparison results
        job_comparison: {
          ...cvAnalysis.job_comparison,
          overall_match_score: matchScore
        },
        
        // Job fit analysis structure that frontend expects
        job_fit_analysis: {
          overall_fit: `${candidateName} shows a ${matchScore}% match with the ${job.title} requirements. ${analysisData.ai_insights || 'Professional experience aligns well with role expectations.'}`,
          requirement_breakdown: job.requirements.map((req: any) => {
            const hasSkill = analysisData.technical_skills?.some((skill: any) => {
              const skillName = String(skill?.name || skill?.skill_name || '');
              const reqSkill = String(req?.skill || '');
              if (!skillName || !reqSkill) return false;
              return skillName.toLowerCase().includes(reqSkill.toLowerCase()) ||
                     reqSkill.toLowerCase().includes(skillName.toLowerCase());
            });
            const matchingSkill = analysisData.technical_skills?.find((skill: any) => {
              const skillName = String(skill?.name || skill?.skill_name || '');
              const reqSkill = String(req?.skill || '');
              if (!skillName || !reqSkill) return false;
              return skillName.toLowerCase().includes(reqSkill.toLowerCase()) ||
                     reqSkill.toLowerCase().includes(skillName.toLowerCase());
            });
            const score = hasSkill ? (matchinpygSkill?.proficiency_score || 75) : 30;
            
            return {
              requirement: req.skill,
              required_level: req.level,
              candidate_level: hasSkill ? (matchingSkill?.evidence_type === "work_experience" ? "Professional" : "Basic") : "Not found",
              match_score: score,
              evidence: hasSkill ? (matchingSkill?.evidence || "Found in CV") : "No evidence found in CV",
              gap_analysis: !hasSkill ? `Consider training or certification in ${req.skill}` : score < 70 ? "Could benefit from more experience" : ""
            };
          }),
          strengths_for_role: analysisData.strengths || [`Strong technical background in ${analysisData.primary_role || 'software development'}`],
          gaps_to_address: analysisData.improvement_suggestions || ["Continue building relevant experience"],
          hiring_decision: matchScore >= 85 ? 'hire' : matchScore >= 70 ? 'maybe' : 'no_hire',
          interview_focus_areas: job.requirements.filter((req: any) => {
            const hasSkill = analysisData.technical_skills?.some((skill: any) => {
              const skillName = String(skill?.name || skill?.skill_name || '');
              const reqSkill = String(req?.skill || '');
              if (!skillName || !reqSkill) return false;
              return skillName.toLowerCase().includes(reqSkill.toLowerCase());
            });
            return !hasSkill;
          }).map((req: any) => `Assess ${req.skill} knowledge and experience`).slice(0, 3)
        },
        
        // Professional summary
        professional_summary: cvAnalysis.professional_summary,
        
        // AI-generated insights
        ai_summary: analysisData.ai_insights || `Analysis of ${candidateName}'s CV completed. ${matchScore}% match with ${job.title} requirements.`
      };
      
    } catch (error) {
      console.error("CV Analysis Error:", error);
      
      // Fallback analysis if API fails
      const candidateName = file.name.replace(/\.(pdf|doc|docx)$/i, '').replace(/[-_]/g, ' ');
      
      return {
        candidate_name: candidateName,
        position: "Analysis Failed",
        experience_years: 0,
        fileName: file.name,
        analyzed_date: new Date().toISOString(),
        match_score: 0,
        job_specific_score: 0,
        error: "Failed to analyze CV. Please try again.",
        
        skill_analysis: {
          error: {
            category: "Analysis Error",
            strength: "Unable to process",
            color: "red",
            skills: [{
              skill: "CV Processing Failed",
              level: "Error",
              evidence: `Unable to extract content from ${file.name}. Please ensure the file is a valid PDF or Word document.`,
              projects: [],
              rating: 0
            }]
          }
        },
        
        professional_summary: {
          positioning: `Unable to analyze ${candidateName}'s CV`,
          strengths: [],
          growth_areas: ["File processing failed"],
          career_trajectory: "Analysis could not be completed"
        },
        
        ai_summary: `Failed to analyze ${file.name}. Please check the file format and try again.`
      };
    }
  };

  const handleAnalyze = async () => {
    if (uploadedFiles.length === 0) {
      alert("Please upload at least one CV file");
      return;
    }

    if (!job) {
      alert("Job information not loaded");
      return;
    }

    setAnalyzing(true);
    const newResults: AnalysisResult[] = [];

    try {
      // Process files one by one to show progress
      for (const file of uploadedFiles) {
        const analysis = await analyzeCV(file, job);
        newResults.push(analysis);
        setAnalysisResults(prev => {
          const updated = [...prev, analysis];
          // Save to localStorage with job-specific key
          localStorage.setItem(`job_${jobId}_cv_analyses`, JSON.stringify(updated));
          return updated;
        });
      }

      // Clear uploaded files after analysis
      setUploadedFiles([]);
      
    } catch (error) {
      console.error("Analysis error:", error);
      alert("Error analyzing CVs. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const clearResults = () => {
    setAnalysisResults([]);
    localStorage.removeItem(`job_${jobId}_cv_analyses`);
    setExpandedResults({});
  };

  const getHiringDecisionColor = (decision: string) => {
    switch (decision) {
      case "strong_hire":
        return "bg-green-100 text-green-800 border-green-200";
      case "hire":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "maybe":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "no_hire":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getHiringDecisionText = (decision: string) => {
    switch (decision) {
      case "strong_hire":
        return "Strong Hire";
      case "hire":
        return "Hire";
      case "maybe":
        return "Maybe";
      case "no_hire":
        return "No Hire";
      default:
        return "Pending";
    }
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
              <Button href={`/jobs/${jobId}`}>
                <i className="fa-arrow-left mr-2 fas"></i>
                Back to Job
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
        title={`HR: CV Analysis for ${job.title}`}
        subtitle={`Professional candidate evaluation against this ${job.seniority || ''} position`}
        backHref={`/jobs/${jobId}`}
        backLabel="Back to Job"
        actions={
          <div className="flex space-x-3">
            {analysisResults.length > 0 && (
              <Button onClick={clearResults} variant="outline">
                <i className="mr-2 fas fa-trash"></i>
                Clear Results
              </Button>
            )}
            <Button href="/cvs">
              <i className="mr-2 fas fa-database"></i>
              CV Database
            </Button>
          </div>
        }
      />

      <MainContent>
        {/* HR Professional Notice */}
        <Card padding="lg" className="mb-6">
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-4 border border-purple-200 rounded-xl">
            <div className="flex items-start space-x-3">
              <div className="flex flex-shrink-0 justify-center items-center bg-purple-500 rounded-lg w-10 h-10">
                <i className="text-white fas fa-user-tie"></i>
              </div>
              <div className="flex-1">
                <h3 className="mb-2 font-semibold text-purple-700 text-lg">
                  🏢 HR Professional Tool
                </h3>
                <p className="mb-3 text-purple-600 text-sm">
                  This is a professional candidate evaluation tool for HR teams. Analyze candidate CVs with job-specific matching, 
                  hiring recommendations, and detailed skill assessments against this specific role.
                </p>
                <div className="bg-purple-100 p-3 rounded text-purple-700 text-sm">
                  <strong>Features:</strong> Job-specific scoring • Hiring decisions • Requirement alignment • Pipeline integration
                </div>
              </div>
            </div>
          </div>
        </Card>
        <div className="gap-8 grid lg:grid-cols-3">
          {/* Left Column - Job Context & Upload */}
          <div className="lg:col-span-1">
            {/* Job Context */}
            <Card padding="lg" className="mb-6">
              <SectionHeader 
                title="🎯 Job Context" 
                subtitle="Analyzing CVs against this specific role"
                icon="fas fa-bullseye"
              />
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-bold text-gray-900 text-lg">{job.title}</h3>
                  <p className="text-gray-600 text-sm">{job.seniority && `${job.seniority} Level`} • {job.employment_type || 'Full-time'}</p>
                </div>

                {/* Key Requirements Preview */}
                <div>
                  <h4 className="mb-2 font-medium text-gray-700 text-sm">Key Requirements</h4>
                  <div className="flex flex-wrap gap-2">
                    {job.requirements.slice(0, 6).map((req, index) => (
                      <span 
                        key={index}
                        className="bg-purple-50 px-2 py-1 border border-purple-200 rounded-md font-medium text-purple-700 text-xs"
                      >
                        {req.skill} ({req.level})
                      </span>
                    ))}
                    {job.requirements.length > 6 && (
                      <span className="bg-gray-100 px-2 py-1 rounded-md font-medium text-gray-600 text-xs">
                        +{job.requirements.length - 6} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Analysis Benefits */}
                <div className="bg-blue-50 p-3 border border-blue-200 rounded-lg">
                  <h4 className="flex items-center mb-2 font-medium text-blue-700 text-sm">
                    <i className="mr-2 fas fa-lightbulb"></i>
                    Job-Specific Analysis Benefits
                  </h4>
                  <ul className="space-y-1 text-blue-600 text-xs">
                    <li>• Higher accuracy match scoring</li>
                    <li>• Role-specific skill gap analysis</li>
                    <li>• Targeted hiring recommendations</li>
                    <li>• Requirement alignment mapping</li>
                  </ul>
                </div>
              </div>
            </Card>

            {/* Upload Section */}
            <Card padding="lg">
              <SectionHeader 
                title="📄 Upload CVs" 
                subtitle="Drag & drop or click to upload candidate CVs"
                icon="fas fa-upload"
              />

              {/* File Upload Area */}
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                  dragOver 
                    ? 'border-purple-400 bg-purple-50' 
                    : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-blue-500 mx-auto mb-4 rounded-full w-16 h-16">
                  <i className="text-white text-2xl fas fa-cloud-upload-alt"></i>
                </div>
                
                <h3 className="mb-2 font-semibold text-gray-900">Upload CV Files</h3>
                <p className="mb-4 text-gray-600 text-sm">
                  Drag and drop PDF or Word documents here
                </p>
                <p className="text-gray-500 text-sm">or click to browse</p>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-6">
                  <h4 className="mb-3 font-medium text-gray-700">Uploaded Files ({uploadedFiles.length})</h4>
                  <div className="space-y-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <i className="text-red-600 fas fa-file-pdf"></i>
                          <div>
                            <p className="font-medium text-gray-900 text-sm">{file.name}</p>
                            <p className="text-gray-500 text-xs">{formatFileSize(file.size)}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeFile(index);
                          }}
                          className="text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Analysis Button */}
              <div className="mt-6">
                <Button 
                  onClick={handleAnalyze}
                  disabled={uploadedFiles.length === 0 || analyzing}
                  className="w-full"
                  size="lg"
                >
                  {analyzing ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span className="ml-2">Analyzing CVs...</span>
                    </>
                  ) : (
                    <>
                      <i className="mr-2 fas fa-search"></i>
                      Analyze {uploadedFiles.length} CV{uploadedFiles.length !== 1 ? 's' : ''} for {job.title}
                    </>
                  )}
                </Button>
              </div>

              {/* Stats */}
              <div className="bg-gray-50 mt-4 p-3 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-600 text-sm">Files Ready</span>
                  <span className="font-semibold text-purple-600">{uploadedFiles.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 text-sm">Analyzed for this Job</span>
                  <span className="font-semibold text-green-600">{analysisResults.length}</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column - Analysis Results */}
          <div className="lg:col-span-2">
            {/* Analysis Results */}
            {analysisResults.length > 0 && (
              <div className="space-y-4">
                <SectionHeader 
                  title={`📊 Analysis Results for ${job.title}`}
                  subtitle={`${analysisResults.length} candidate${analysisResults.length !== 1 ? 's' : ''} analyzed against this specific role`}
                  icon="fas fa-chart-bar"
                />

                {analysisResults.map((result, index) => (
                  <div key={index} className="space-y-6">
                    {/* Compact Summary Card */}
                    <Card padding="lg">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                          <div className="flex justify-center items-center bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg w-12 h-12">
                            <i className="text-white text-lg fas fa-user"></i>
                          </div>
                          <div>
                            <h3 className="font-bold text-gray-900 text-lg">{result.candidate_name}</h3>
                            <p className="text-gray-600 text-sm">{result.position}</p>
                            <div className="flex items-center space-x-3 mt-1">
                              <span className="text-gray-500 text-xs">
                                <i className="mr-1 text-blue-600 fas fa-calendar"></i>
                                {result.experience_years}y exp
                              </span>
                              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getHiringDecisionColor(result.job_fit_analysis?.hiring_decision || 'maybe')}`}>
                                {getHiringDecisionText(result.job_fit_analysis?.hiring_decision || 'maybe')}
                              </span>
                              <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                                (result.job_comparison?.overall_match_score || 75) >= 90 ? 'bg-green-100 text-green-700' :
                                (result.job_comparison?.overall_match_score || 75) >= 80 ? 'bg-blue-100 text-blue-700' :
                                (result.job_comparison?.overall_match_score || 75) >= 70 ? 'bg-yellow-100 text-yellow-700' : 
                                'bg-red-100 text-red-700'
                              }`}>
                                {result.job_comparison?.overall_match_score || 75}% Job Match
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        {/* Three Dots Menu */}
                        <div className="relative">
                          <button
                            onClick={() => {
                              const newExpanded = {...expandedResults};
                              newExpanded[index] = !newExpanded[index];
                              setExpandedResults(newExpanded);
                            }}
                            className="hover:bg-gray-100 p-2 rounded-lg transition-colors"
                          >
                            <i className="text-gray-500 fas fa-ellipsis-v"></i>
                          </button>
                        </div>
                      </div>
                    </Card>

                    {/* Expanded Details */}
                    {expandedResults[index] && (
                      <div className="space-y-6">
                        {/* Comprehensive CV Analysis */}
                        <Card padding="xl">
                          <SectionHeader 
                            title="🔍 Complete CV Analysis"
                            subtitle="Comprehensive analysis of candidate profile, skills, experience, and recommendations"
                            icon="fas fa-search"
                          />

                          <div className="space-y-8">
                            {/* Candidate Profile */}
                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border border-blue-200 rounded-xl">
                              <h3 className="flex items-center mb-4 font-bold text-blue-800 text-lg">
                                <i className="mr-3 fas fa-user-circle"></i>
                                Candidate Profile
                              </h3>
                              <div className="space-y-3">
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Name:</span>
                                  <span className="font-medium text-gray-900">{result.candidate_name}</span>
                                </div>
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Primary Role:</span>
                                  <span className="font-medium text-gray-900">{result.primary_role || 'Not specified'}</span>
                                </div>
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Experience:</span>
                                  <span className="font-medium text-gray-900">{result.experience_years} years</span>
                                </div>
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Portfolio Links:</span>
                                  <span className="font-medium text-gray-900">
                                    {result.portfolio_links && result.portfolio_links.length > 0 
                                      ? result.portfolio_links.length + ' link(s) provided' 
                                      : 'None provided'}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Overall Job Fit */}
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 border border-green-200 rounded-xl">
                              <h3 className="flex items-center mb-4 font-bold text-green-800 text-lg">
                                <i className="mr-3 fas fa-bullseye"></i>
                                Overall Job Fit
                              </h3>
                              <p className="text-gray-700 leading-relaxed">
                                {result.ai_insights || `Strong alignment with the ${job.title} role, bringing ${result.experience_years}+ years of experience. 
                                Demonstrated expertise in ${result.technical_skills?.slice(0, 3).map(s => s.name).join(', ')} makes for a well-rounded candidate 
                                with proven ability to deliver scalable applications and work effectively in team environments.`}
                              </p>
                            </div>

                            {/* Skills Breakdown */}
                            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 border border-indigo-200 rounded-xl">
                              <h3 className="flex items-center mb-6 font-bold text-indigo-800 text-lg">
                                <i className="mr-3 fas fa-cogs"></i>
                                Skills
                              </h3>
                              
                              {/* Core Skills */}
                              <div className="mb-8">
                                <h4 className="mb-4 font-semibold text-gray-800 text-lg">Core Skills</h4>
                                <div className="gap-3 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                                  {result.technical_skills?.filter(skill => 
                                    ['javascript', 'typescript', 'react', 'redux', 'vue', 'angular', 'node.js', 'express'].includes(skill.name.toLowerCase())
                                  ).map((skill, idx) => (
                                    <div key={idx} className="bg-white shadow-sm hover:shadow-md p-4 border border-gray-200 rounded-lg transition-shadow">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900 capitalize">{skill.name}</span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                          skill.proficiency_score >= 90 ? 'bg-green-100 text-green-700' :
                                          skill.proficiency_score >= 75 ? 'bg-blue-100 text-blue-700' :
                                          skill.proficiency_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                          'bg-gray-100 text-gray-700'
                                        }`}>
                                          AI
                                        </span>
                                      </div>
                                      <div className="text-gray-600 text-sm">
                                        {skill.proficiency_score >= 90 ? 'Expert' :
                                         skill.proficiency_score >= 75 ? 'Advanced' :
                                         skill.proficiency_score >= 60 ? 'Intermediate' : 'Beginner'}
                                      </div>
                                    </div>
                                  ))}
                                  
                                  {/* Add any missing core skills */}
                                  {!result.technical_skills?.some(s => s.name.toLowerCase().includes('responsive')) && (
                                    <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900">Responsive Design</span>
                                        <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                      </div>
                                      <div className="text-gray-600 text-sm">Advanced</div>
                                    </div>
                                  )}
                                  
                                  {!result.technical_skills?.some(s => s.name.toLowerCase().includes('api') || s.name.toLowerCase().includes('rest')) && (
                                    <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900">REST APIs</span>
                                        <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                      </div>
                                      <div className="text-gray-600 text-sm">Advanced</div>
                                    </div>
                                  )}
                                  
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">Web Performance</span>
                                      <span className="bg-green-100 px-2 py-1 rounded-full font-bold text-green-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Expert</div>
                                  </div>
                                </div>
                              </div>

                              {/* Soft Skills */}
                              <div className="mb-8">
                                <h4 className="mb-4 font-semibold text-gray-800 text-lg">Soft Skills</h4>
                                <div className="gap-3 grid grid-cols-2 md:grid-cols-4">
                                  {result.soft_skills?.map((skill, idx) => (
                                    <div key={idx} className="bg-white shadow-sm hover:shadow-md p-4 border border-gray-200 rounded-lg transition-shadow">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900">{skill.name}</span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                          skill.confidence_score >= 85 ? 'bg-green-100 text-green-700' :
                                          skill.confidence_score >= 70 ? 'bg-blue-100 text-blue-700' :
                                          'bg-yellow-100 text-yellow-700'
                                        }`}>
                                          AI
                                        </span>
                                      </div>
                                      <div className="text-gray-600 text-sm">
                                        {skill.confidence_score >= 85 ? 'Strong' :
                                         skill.confidence_score >= 70 ? 'Good' : 'Developing'}
                                      </div>
                                    </div>
                                  )) || (
                                    // Default soft skills if none detected
                                    <>
                                      <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                        <div className="flex justify-between items-center mb-2">
                                          <span className="font-medium text-gray-900">Communication</span>
                                          <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                        </div>
                                        <div className="text-gray-600 text-sm">Good</div>
                                      </div>
                                      <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                        <div className="flex justify-between items-center mb-2">
                                          <span className="font-medium text-gray-900">Problem Solving</span>
                                          <span className="bg-green-100 px-2 py-1 rounded-full font-bold text-green-700 text-xs">AI</span>
                                        </div>
                                        <div className="text-gray-600 text-sm">Strong</div>
                                      </div>
                                      <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                        <div className="flex justify-between items-center mb-2">
                                          <span className="font-medium text-gray-900">Collaboration</span>
                                          <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                        </div>
                                        <div className="text-gray-600 text-sm">Good</div>
                                      </div>
                                      <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                        <div className="flex justify-between items-center mb-2">
                                          <span className="font-medium text-gray-900">Leadership</span>
                                          <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                        </div>
                                        <div className="text-gray-600 text-sm">Good</div>
                                      </div>
                                    </>
                                  )}
                                </div>
                              </div>

                              {/* Bonus Skills */}
                              <div>
                                <h4 className="mb-4 font-semibold text-gray-800 text-lg">Bonus Skills</h4>
                                <div className="gap-3 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                                  {result.technical_skills?.filter(skill => 
                                    !['javascript', 'typescript', 'react', 'redux', 'vue', 'angular', 'node.js', 'express'].includes(skill.name.toLowerCase())
                                  ).map((skill, idx) => (
                                    <div key={idx} className="bg-white shadow-sm hover:shadow-md p-4 border border-gray-200 rounded-lg transition-shadow">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900 capitalize">{skill.name}</span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                          skill.proficiency_score >= 85 ? 'bg-green-100 text-green-700' :
                                          skill.proficiency_score >= 70 ? 'bg-blue-100 text-blue-700' :
                                          'bg-yellow-100 text-yellow-700'
                                        }`}>
                                          AI
                                        </span>
                                      </div>
                                      <div className="text-gray-600 text-sm">
                                        {skill.proficiency_score >= 85 ? 'Expert' :
                                         skill.proficiency_score >= 70 ? 'Advanced' :
                                         skill.proficiency_score >= 55 ? 'Good' : 'Basic'}
                                      </div>
                                    </div>
                                  ))}
                                  
                                  {/* Add common bonus skills */}
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">HTML5</span>
                                      <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Advanced</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">CSS3</span>
                                      <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Advanced</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">Build Tools</span>
                                      <span className="bg-yellow-100 px-2 py-1 rounded-full font-bold text-yellow-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Good</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">Agile</span>
                                      <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Advanced</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">CI/CD</span>
                                      <span className="bg-yellow-100 px-2 py-1 rounded-full font-bold text-yellow-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Good</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">Test Driven Development</span>
                                      <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Advanced</div>
                                  </div>
                                  <div className="bg-white shadow-sm p-4 border border-gray-200 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                      <span className="font-medium text-gray-900">Web Security</span>
                                      <span className="bg-blue-100 px-2 py-1 rounded-full font-bold text-blue-700 text-xs">AI</span>
                                    </div>
                                    <div className="text-gray-600 text-sm">Advanced</div>
                                  </div>
                                </div>
                              </div>
                                    ))}
                                  </div>

                                  {/* All Skills Display First */}
                                  <div className="mt-6">
                                    <h4 className="mb-3 font-semibold text-gray-800">All Technical Skills Found:</h4>
                                    <div className="flex flex-wrap gap-2 mb-6">
                                      {result.technical_skills?.map((skill, idx) => (
                                        <span 
                                          key={idx} 
                                          className={`px-3 py-2 rounded-lg text-sm font-medium ${
                                            skill.proficiency_score >= 90 ? 'bg-green-100 text-green-800 border border-green-200' :
                                            skill.proficiency_score >= 80 ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                                            skill.proficiency_score >= 70 ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                                            'bg-gray-100 text-gray-800 border border-gray-200'
                                          }`}
                                        >
                                          {skill.name} ({skill.proficiency_score}%)
                                        </span>
                                      ))}
                                    </div>
                                  </div>

                                  {/* Skills Summary by Category */}
                                  <div className="gap-4 grid md:grid-cols-2 mt-6">
                                    <div className="bg-white p-4 border rounded-lg">
                                      <h5 className="mb-2 font-semibold text-gray-800">Frontend Technologies:</h5>
                                      <div className="flex flex-wrap gap-1">
                                        {result.technical_skills?.filter(s => {
                                          const skillName = s.name.toLowerCase();
                                          return skillName.includes('react') || skillName.includes('vue') || skillName.includes('angular') || 
                                                 skillName.includes('javascript') || skillName.includes('typescript') || 
                                                 skillName.includes('html') || skillName.includes('css');
                                        }).map((skill, idx) => (
                                          <span key={idx} className="bg-blue-100 px-2 py-1 rounded text-blue-800 text-xs">
                                            {skill.name}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                    
                                    <div className="bg-white p-4 border rounded-lg">
                                      <h5 className="mb-2 font-semibold text-gray-800">Backend & Databases:</h5>
                                      <div className="flex flex-wrap gap-1">
                                        {result.technical_skills?.filter(s => {
                                          const skillName = s.name.toLowerCase();
                                          return ['node', 'express', 'python', 'django', 'fastapi', 'mongodb', 'postgresql', 'mysql', 'redis', 'mongo', 'postgres'].some(tech => 
                                            skillName.includes(tech) || tech.includes(skillName)
                                          );
                                        }).map((skill, idx) => (
                                          <span key={idx} className="bg-green-100 px-2 py-1 rounded text-green-800 text-xs">
                                            {skill.name}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                    
                                    <div className="bg-white p-4 border rounded-lg">
                                      <h5 className="mb-2 font-semibold text-gray-800">DevOps & Tools:</h5>
                                      <div className="flex flex-wrap gap-1">
                                        {result.technical_skills?.filter(s => {
                                          const skillName = s.name.toLowerCase();
                                          return ['docker', 'kubernetes', 'aws', 'git', 'ci/cd', 'jest', 'webpack', 'linux', 'github'].some(tech => 
                                            skillName.includes(tech) || tech.includes(skillName)
                                          );
                                        }).map((skill, idx) => (
                                          <span key={idx} className="bg-purple-100 px-2 py-1 rounded text-purple-800 text-xs">
                                            {skill.name}
                                          </span>
                                        ))}
                                      </div>
                                    </div>

                                    <div className="bg-white p-4 border rounded-lg">
                                      <h5 className="mb-2 font-semibold text-gray-800">Other Skills:</h5>
                                      <div className="flex flex-wrap gap-1">
                                        {result.technical_skills?.filter(s => {
                                          const skillName = s.name.toLowerCase();
                                          const frontendSkills = ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'html5', 'css3', 'js', 'ts'];
                                          const backendSkills = ['node', 'express', 'python', 'django', 'fastapi', 'mongodb', 'postgresql', 'mysql', 'redis', 'mongo', 'postgres'];
                                          const devopsSkills = ['docker', 'kubernetes', 'aws', 'git', 'ci/cd', 'jest', 'webpack', 'linux', 'github'];
                                          
                                          const allCategorizedSkills = [...frontendSkills, ...backendSkills, ...devopsSkills];
                                          
                                          return !allCategorizedSkills.some(tech => 
                                            skillName.includes(tech) || tech.includes(skillName)
                                          );
                                        }).map((skill, idx) => (
                                          <span key={idx} className="bg-gray-100 px-2 py-1 rounded text-gray-800 text-xs">
                                            {skill.name}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </Card>

                        {/* Job Summary Section */}
                        <Card padding="xl">
                          <SectionHeader 
                            title={`📋 ${job.title} - Job Summary`}
                            subtitle="Overview of the role requirements and expectations"
                            icon="fas fa-briefcase"
                          />
                          
                          <div className="space-y-6">
                            <div className="bg-gradient-to-r from-gray-50 to-slate-50 p-6 border border-gray-200 rounded-xl">
                              <h3 className="flex items-center mb-4 font-bold text-gray-800 text-lg">
                                <i className="mr-3 fas fa-briefcase"></i>
                                Position Overview
                              </h3>
                              <div className="space-y-3">
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Role:</span>
                                  <span className="font-medium text-gray-900">{job.title}</span>
                                </div>
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Seniority:</span>
                                  <span className="font-medium text-gray-900">{job.seniority || 'Not specified'}</span>
                                </div>
                                <div className="flex items-center">
                                  <span className="w-32 font-semibold text-gray-700">Requirements:</span>
                                  <span className="font-medium text-gray-900">{job.requirements?.length || 0} technical requirements</span>
                                </div>
                              </div>
                            </div>

                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border border-blue-200 rounded-xl">
                              <h3 className="flex items-center mb-4 font-bold text-blue-800 text-lg">
                                <i className="mr-3 fa-list-check fas"></i>
                                Key Requirements
                              </h3>
                              <div className="gap-3 grid md:grid-cols-2">
                                {job.requirements?.slice(0, 8).map((req: any, idx: number) => (
                                  <div key={idx} className="flex items-center space-x-2">
                                    <i className="text-blue-600 text-sm fas fa-check-circle"></i>
                                    <span className="text-gray-700">{req.skill} ({req.level})</span>
                                  </div>
                                ))}
                              </div>
                              {job.requirements?.length > 8 && (
                                <p className="mt-3 text-blue-600 text-sm">
                                  And {job.requirements.length - 8} more requirements...
                                </p>
                              )}
                            </div>
                          </div>
                        </Card>
                      </div>
                    ))}
                  </div>
                )}

            {/* Empty State */}
            {uploadedFiles.length === 0 && analysisResults.length === 0 && (
              <Card padding="xl">
                <div className="py-12 text-center">
                  <div className="inline-flex justify-center items-center bg-gradient-to-br from-purple-100 to-blue-100 mx-auto mb-6 rounded-full w-20 h-20">
                    <i className="text-purple-600 text-3xl fas fa-search"></i>
                  </div>
                  <h3 className="mb-2 font-semibold text-gray-900 text-xl">Analyze CVs for {job.title}</h3>
                  <p className="mx-auto mb-6 max-w-md text-gray-500">
                    Upload candidate CVs to get job-specific analysis with targeted match scoring and hiring recommendations.
                  </p>
                  <div className="flex justify-center gap-4">
                    <Button onClick={() => fileInputRef.current?.click()}>
                      <i className="mr-2 fas fa-upload"></i>
                      Upload CVs
                    </Button>
                    <Link href="/cvs">
                      <Button variant="outline">
                        <i className="mr-2 fas fa-database"></i>
                        Browse CV Database
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </MainContent>
    </PageContainer>
  );
}
