"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { 
  AppHeader, PageContainer, MainContent, Card, Button, SectionHeader, LoadingSpinner, ErrorDisplay 
} from "@/components/shared";

export default function CVAnalyzerPage() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>("");
  const [availableJobs, setAvailableJobs] = useState<any[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<'single' | 'batch'>('single');
  const [expandedResults, setExpandedResults] = useState<{[key: number]: boolean}>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Drag and drop handlers
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => 
      file.type === "application/pdf" || 
      file.type === "application/msword" ||
      file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    );
    
    setUploadedFiles(prev => [...prev, ...validFiles]);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setUploadedFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Save CV-Job association for later retrieval
  const saveCVJobAssociation = (cvResult: any, jobId: string) => {
    const associations = JSON.parse(localStorage.getItem('cv_job_associations') || '{}');
    if (!associations[jobId]) {
      associations[jobId] = [];
    }
    
    // Add this CV to the job's associated CVs
    associations[jobId].push({
      ...cvResult,
      associatedAt: new Date().toISOString()
    });
    
    localStorage.setItem('cv_job_associations', JSON.stringify(associations));
  };

  // Toggle expanded details for a result
  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  // Load available jobs
  const loadJobs = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://127.0.0.1:8000/users/me/jobs", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const jobs = await res.json();
        setAvailableJobs(jobs);
      } else {
        // Fallback to mock data if API fails
        setAvailableJobs([
          { id: "1", title: "Senior Frontend Developer" },
          { id: "2", title: "Full Stack Engineer" },
          { id: "3", title: "React Developer" }
        ]);
      }
    } catch (error) {
      console.error("Failed to load jobs:", error);
      // Set mock data for demonstration
      setAvailableJobs([
        { id: "1", title: "Senior Frontend Developer" },
        { id: "2", title: "Full Stack Engineer" },
        { id: "3", title: "React Developer" }
      ]);
    }
  };

  // Enhanced AI-powered CV analysis with detailed breakdown
  const analyzeCV = async (file: File, jobId?: string) => {
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
      
      // Step 2: Get AI analysis of the CV content
      const analysisResponse = await fetch('http://127.0.0.1:8000/cvs/analyze-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cv_text: cvText,
          job_id: jobId || null,
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
      
      // If job comparison is requested, get job details and compare
      let jobComparisonData = null;
      if (jobId && jobId !== "") {
        try {
          const token = localStorage.getItem("access_token");
          const jobResponse = await fetch(`http://127.0.0.1:8000/users/me/jobs/${jobId}`, {
            headers: {
              "Authorization": `Bearer ${token}`,
            },
          });
          
          if (jobResponse.ok) {
            const jobData = await jobResponse.json();
            
            // Compare CV skills against job requirements
            jobComparisonData = {
              job_title: jobData.title,
              job_requirements: jobData.requirements,
              requirement_matches: jobData.requirements.map((req: any) => {
                const hasSkill = analysisData.skills?.some((skill: any) => 
                  skill.name.toLowerCase().includes(req.skill.toLowerCase()) ||
                  req.skill.toLowerCase().includes(skill.name.toLowerCase())
                );
                return {
                  requirement: req.skill,
                  required_level: req.level,
                  has_skill: hasSkill,
                  candidate_level: hasSkill ? "Found in CV" : "Not mentioned",
                  match_status: hasSkill ? "✅" : "❌",
                  evidence: hasSkill ? `Mentioned in CV content` : "No evidence found in CV"
                };
              })
            };
          }
        } catch (error) {
          console.error("Error fetching job data:", error);
        }
      }
      
      return {
        candidate_name: candidateName,
        position: analysisData.position || "Not specified",
        experience_years: experienceYears,
        fileName: file.name,
        analyzed_date: new Date().toISOString(),
        
        // Real skills extracted from CV
        skill_analysis: analysisData.skill_analysis || {
          extracted_skills: {
            category: "Extracted Skills",
            strength: "Identified from CV",
            color: "blue",
            skills: (analysisData.skills || []).map((skill: any) => ({
              skill: skill.name,
              level: skill.level || "Mentioned",
              evidence: skill.evidence || `Found in CV: ${skill.context || ''}`,
              projects: skill.projects || [],
              rating: skill.proficiency_score || 50
            }))
          }
        },
        
        // Job comparison results if available
        job_comparison: jobComparisonData,
        
        // Professional summary from AI analysis
        professional_summary: {
          positioning: analysisData.summary || `${candidateName} - Professional background extracted from CV`,
          strengths: analysisData.strengths || [],
          growth_areas: analysisData.growth_areas || [],
          career_trajectory: analysisData.career_trajectory || "Career progression details extracted from CV"
        },
        
        // AI-generated insights
        ai_summary: analysisData.ai_summary || `Analysis of ${candidateName}'s CV completed. ${analysisData.skills?.length || 0} skills identified with ${experienceYears} years of experience.`
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
    if (uploadedFiles.length === 0) return;
    
    setIsAnalyzing(true);
    const results = [];

    try {
      for (const file of uploadedFiles) {
        const analysis = await analyzeCV(file, selectedJob);
        if (analysis) {
          const result = {
            fileName: file.name,
            fileSize: file.size,
            ...analysis
          };
          
          results.push(result);
          
          // Save CV-Job association if a job is selected
          if (selectedJob) {
            saveCVJobAssociation(result, selectedJob);
          }
        }
      }
      
      setAnalysisResults(results);
    } catch (error) {
      console.error("Batch analysis error:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Load jobs on component mount
  useEffect(() => {
    loadJobs();
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getSkillColor = (category: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      green: 'bg-green-100 text-green-800 border-green-200', 
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
      red: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[category as keyof typeof colors] || colors.blue;
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 90) return 'bg-green-500';
    if (rating >= 80) return 'bg-blue-500';
    if (rating >= 70) return 'bg-yellow-500';
    if (rating >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const SkillCard = ({ skill, categoryColor }: { skill: any, categoryColor: string }) => {
    const [showTooltip, setShowTooltip] = useState(false);

    return (
      <div 
        className="relative"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <div className={`${getSkillColor(categoryColor)} border px-3 py-2 rounded-lg cursor-pointer transition-all hover:shadow-md hover:scale-105`}>
          <div className="flex justify-between items-center">
            <span className="font-medium text-sm">{skill.skill}</span>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${getRatingColor(skill.rating)}`}></div>
              <span className="font-semibold text-xs">{skill.rating}%</span>
            </div>
          </div>
          <div className="opacity-75 mt-1 text-xs">{skill.level}</div>
        </div>

        {/* Detailed Tooltip */}
        {showTooltip && (
          <div className="top-full left-0 z-50 absolute bg-white shadow-xl mt-2 p-4 border rounded-lg w-80">
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold text-gray-900">{skill.skill}</h4>
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getSkillColor(categoryColor)}`}>
                  {skill.level}
                </span>
              </div>
              
              <div>
                <h5 className="mb-1 font-medium text-gray-700 text-sm">Evidence:</h5>
                <p className="text-gray-600 text-sm">{skill.evidence}</p>
              </div>
              
              {skill.projects && skill.projects.length > 0 && (
                <div>
                  <h5 className="mb-1 font-medium text-gray-700 text-sm">Projects:</h5>
                  <div className="flex flex-wrap gap-1">
                    {skill.projects.map((project: string, idx: number) => (
                      <span key={idx} className="bg-gray-100 px-2 py-1 rounded text-gray-700 text-xs">
                        {project}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getRatingColor(skill.rating)}`}
                    style={{ width: `${skill.rating}%` }}
                  ></div>
                </div>
                <span className="ml-2 font-semibold text-gray-700 text-sm">{skill.rating}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <PageContainer>
      <AppHeader 
        title="Personal CV Analyzer"
        subtitle="Analyze your CV to understand your skills and career potential"
        backHref="/cvs"
        backLabel="Back to CVs"
        actions={
          <div className="flex space-x-3">
            <Link href="/jobs">
              <Button variant="outline">
                <i className="mr-2 fas fa-briefcase"></i>
                Browse Jobs
              </Button>
            </Link>
          </div>
        }
      />

      <MainContent>
        <div className="gap-8 grid lg:grid-cols-4">
          {/* Upload Sidebar */}
          <div className="lg:col-span-1">
            {/* Personal Analysis Notice */}
            <Card padding="lg" className="mb-6">
              <div className="bg-gradient-to-r from-blue-50 to-green-50 p-4 border border-blue-200 rounded-xl">
                <div className="flex items-start space-x-3">
                  <div className="flex flex-shrink-0 justify-center items-center bg-blue-500 rounded-lg w-8 h-8">
                    <i className="text-white text-sm fas fa-user"></i>
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-2 font-semibold text-blue-700 text-sm">
                      � Personal CV Analysis
                    </h3>
                    <p className="mb-3 text-blue-600 text-xs">
                      This tool analyzes your CV to help you understand your skills, experience level, and career potential. Perfect for job seekers and career planning.
                    </p>
                    <div className="bg-blue-100 p-2 rounded text-blue-700 text-xs">
                      <strong>Note:</strong> HR professionals should use job-specific analysis tools for candidate evaluation.
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <Card padding="lg" className="top-4 sticky">
              <SectionHeader 
                title="Analysis Options" 
                icon="fas fa-cogs"
                size="sm"
              />
              
              <div className="space-y-4">
                {/* Analysis Mode */}
                <div>
                  <label className="block mb-3 font-medium text-gray-700 text-sm">Analysis Type</label>
                  <div className="space-y-3">
                    <label className="flex items-start">
                      <input 
                        type="radio" 
                        name="mode" 
                        value="single"
                        checked={analysisMode === 'single'}
                        onChange={(e) => setAnalysisMode(e.target.value as 'single')}
                        className="mt-1 mr-3 text-blue-600"
                      />
                      <div>
                        <span className="font-medium text-gray-900 text-sm">Personal CV Review</span>
                        <p className="mt-1 text-gray-600 text-xs">Analyze your CV to understand your skills and improve your profile</p>
                      </div>
                    </label>
                    <label className="flex items-start">
                      <input 
                        type="radio" 
                        name="mode" 
                        value="batch"
                        checked={analysisMode === 'batch'}
                        onChange={(e) => setAnalysisMode(e.target.value as 'batch')}
                        className="mt-1 mr-3 text-blue-600"
                      />
                      <div>
                        <span className="font-medium text-gray-900 text-sm">Multiple CV Comparison</span>
                        <p className="mt-1 text-gray-600 text-xs">Compare different versions of your CV or analyze multiple profiles</p>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Career Focus */}
                <div>
                  <label className="block mb-2 font-medium text-gray-700 text-sm">
                    <i className="mr-2 text-blue-600 fas fa-target"></i>
                    Career Focus (Optional)
                  </label>
                  <select 
                    className="bg-white shadow px-3 py-2 border border-gray-300 focus:border-blue-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 w-full text-black text-sm" 
                    value={selectedJob}
                    onChange={(e) => setSelectedJob(e.target.value)}
                  >
                    <option value="">General Career Analysis</option>
                    {availableJobs.map((job) => (
                      <option key={job.id} value={job.id}>Target: {job.title}</option>
                    ))}
                  </select>
                  <p className="mt-1 text-gray-500 text-xs">
                    Select a target role to see how well your CV aligns with that position
                  </p>
                </div>

                {/* Stats */}
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600 text-sm">CVs Ready</span>
                    <span className="font-semibold text-blue-600">{uploadedFiles.length}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Analyzed</span>
                    <span className="font-semibold text-green-600">{analysisResults.length}</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="space-y-6 lg:col-span-3">
            {/* Upload Area */}
            <Card padding="xl">
              <SectionHeader 
                title="Upload CVs" 
                icon="fas fa-cloud-upload-alt"
                subtitle="Drag and drop or click to select PDF/DOC files"
              />

              <div className="space-y-6">
                {/* Drag & Drop Zone */}
                <div
                  className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
                    dragActive 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="space-y-4">
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${
                      dragActive ? 'bg-purple-100' : 'bg-gray-100'
                    }`}>
                      <i className={`text-2xl ${
                        dragActive ? 'text-purple-600 fas fa-download' : 'text-gray-400 fas fa-file-upload'
                      }`}></i>
                    </div>
                    
                    <div>
                      <p className="font-medium text-gray-900 text-lg">
                        {dragActive ? 'Drop files here' : 'Drag & drop CV files here'}
                      </p>
                      <p className="text-gray-500">or click to browse</p>
                      <p className="mt-2 text-gray-400 text-sm">Supports PDF, DOC, DOCX files up to 10MB</p>
                    </div>
                  </div>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-gray-700">
                      <i className="mr-2 text-blue-600 fas fa-list"></i>
                      Uploaded Files ({uploadedFiles.length})
                    </h4>
                    
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex justify-between items-center bg-gray-50 hover:bg-gray-100 p-3 rounded-lg transition-colors">
                          <div className="flex items-center space-x-3">
                            <i className="text-red-500 fas fa-file-pdf"></i>
                            <div>
                              <p className="font-medium text-gray-900 text-sm">{file.name}</p>
                              <p className="text-gray-500 text-xs">{formatFileSize(file.size)}</p>
                            </div>
                          </div>
                          
                          <button
                            onClick={() => removeFile(index)}
                            className="flex justify-center items-center bg-red-100 hover:bg-red-200 rounded-full w-6 h-6 text-red-600 hover:text-red-700 text-sm transition-colors"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analyze Button */}
                {uploadedFiles.length > 0 && (
                  <Button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="w-full"
                    size="lg"
                  >
                    {isAnalyzing ? (
                      <>
                        <i className="mr-2 fas fa-spinner fa-spin"></i>
                        Analyzing Your CV...
                      </>
                    ) : (
                      <>
                        <i className="mr-2 fas fa-user-search"></i>
                        Analyze My CV{uploadedFiles.length > 1 ? 's' : ''}
                      </>
                    )}
                  </Button>
                )}
              </div>
            </Card>

            {/* Analysis Results */}
            {analysisResults.length > 0 && (
              <div className="space-y-4">
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
                              {result.match_score && (
                                <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                                  result.match_score >= 80 ? 'bg-green-100 text-green-700' :
                                  result.match_score >= 60 ? 'bg-yellow-100 text-yellow-700' : 
                                  'bg-red-100 text-red-700'
                                }`}>
                                  {result.match_score}% Match
                                </span>
                              )}
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
                        {/* Job Requirements Comparison */}
                        {result.job_comparison && (
                          <Card padding="xl">
                            <SectionHeader 
                              title={`🎯 ${result.job_comparison.job_title} Requirements Check`}
                              icon="fas fa-tasks"
                              subtitle="How your CV aligns with the specific job requirements"
                            />

                            <div className="space-y-4">
                              {result.job_comparison.requirement_matches.map((req: any, reqIndex: number) => (
                                <div key={reqIndex} className={`p-4 rounded-lg border-2 ${req.has_skill ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                                  <div className="flex justify-between items-start">
                                    <div className="flex items-start space-x-3">
                                      <span className="text-2xl">
                                        {req.match_status}
                                      </span>
                                      <div>
                                        <h4 className="font-semibold text-gray-900">{req.requirement}</h4>
                                        <p className="text-gray-600 text-sm">Required Level: {req.required_level}</p>
                                        <p className="text-gray-600 text-sm">Your Level: {req.candidate_level}</p>
                                      </div>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                      req.has_skill ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                      {req.has_skill ? 'Found' : 'Missing'}
                                    </span>
                                  </div>
                                  <div className="mt-3">
                                    <p className="text-gray-700 text-sm">
                                      <strong>Evidence:</strong> {req.evidence}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>

                            {/* Overall Match Summary */}
                            <div className="bg-blue-50 mt-6 p-4 border border-blue-200 rounded-lg">
                              <h4 className="mb-2 font-semibold text-blue-900">📈 Overall Assessment</h4>
                              <div className="gap-4 grid grid-cols-1 md:grid-cols-3">
                                <div className="text-center">
                                  <div className="font-bold text-green-600 text-2xl">
                                    {result.job_comparison.requirement_matches.filter((req: any) => req.has_skill).length}
                                  </div>
                                  <div className="text-gray-600 text-sm">Requirements Met</div>
                                </div>
                                <div className="text-center">
                                  <div className="font-bold text-red-600 text-2xl">
                                    {result.job_comparison.requirement_matches.filter((req: any) => !req.has_skill).length}
                                  </div>
                                  <div className="text-gray-600 text-sm">Requirements Missing</div>
                                </div>
                                <div className="text-center">
                                  <div className="font-bold text-blue-600 text-2xl">
                                    {Math.round((result.job_comparison.requirement_matches.filter((req: any) => req.has_skill).length / result.job_comparison.requirement_matches.length) * 100)}%
                                  </div>
                                  <div className="text-gray-600 text-sm">Match Rate</div>
                                </div>
                              </div>
                            </div>
                          </Card>
                        )}

                        {/* Skill Proficiency Map */}
                        {result.skill_analysis && (
                          <Card padding="xl">
                            <SectionHeader 
                              title="📊 Skill Proficiency Map" 
                              icon="fas fa-chart-bar"
                              subtitle="Detailed breakdown of technical and soft skills with evidence"
                            />

                            <div className="space-y-8">
                              {Object.entries(result.skill_analysis).map(([categoryKey, category]: [string, any]) => (
                                <div key={categoryKey}>
                                  <div className="flex justify-between items-center mb-4">
                                    <div>
                                      <h3 className="font-bold text-gray-900 text-lg">
                                        🔹 {category.category}
                                      </h3>
                                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSkillColor(category.color)}`}>
                                        {category.strength}
                                      </span>
                                    </div>
                                  </div>
                                  
                                  <div className="gap-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                                    {category.skills.map((skill: any, skillIndex: number) => (
                                      <SkillCard 
                                        key={skillIndex} 
                                        skill={skill} 
                                        categoryColor={category.color}
                                      />
                                    ))}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </Card>
                        )}

                        {/* Job Role Alignment */}
                        {result.role_alignment && (
                          <Card padding="xl">
                            <SectionHeader 
                              title="🎯 Job Role Alignment" 
                              icon="fas fa-bullseye"
                              subtitle="Career fit analysis and growth recommendations"
                            />

                            <div className="space-y-6">
                              {/* High Match Roles */}
                              <div>
                                <h3 className="flex items-center mb-4 font-semibold text-green-700 text-lg">
                                  ✅ High Match Roles (Best Fit Today)
                                </h3>
                                <div className="space-y-3">
                                  {result.role_alignment.high_match.map((role: any, idx: number) => (
                                    <div key={idx} className="flex justify-between items-center bg-green-50 p-4 border border-green-200 rounded-lg">
                                      <div>
                                        <h4 className="font-semibold text-gray-900">{role.role}</h4>
                                        <p className="text-gray-600 text-sm">{role.reason}</p>
                                      </div>
                                      <div className="bg-green-100 px-3 py-1 rounded-full font-bold text-green-700">
                                        {role.match}%
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* Medium Match Roles */}
                              <div>
                                <h3 className="flex items-center mb-4 font-semibold text-yellow-700 text-lg">
                                  ⚡ Medium Match Roles (With Some Growth)
                                </h3>
                                <div className="space-y-3">
                                  {result.role_alignment.medium_match.map((role: any, idx: number) => (
                                    <div key={idx} className="flex justify-between items-center bg-yellow-50 p-4 border border-yellow-200 rounded-lg">
                                      <div>
                                        <h4 className="font-semibold text-gray-900">{role.role}</h4>
                                        <p className="text-gray-600 text-sm">{role.reason}</p>
                                      </div>
                                      <div className="bg-yellow-100 px-3 py-1 rounded-full font-bold text-yellow-700">
                                        {role.match}%
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* Growth Areas */}
                              <div>
                                <h3 className="flex items-center mb-4 font-semibold text-blue-700 text-lg">
                                  🌱 Future Path Roles (Long-Term Growth)
                                </h3>
                                <div className="space-y-3">
                                  {result.role_alignment.growth_areas.map((role: any, idx: number) => (
                                    <div key={idx} className="flex justify-between items-center bg-blue-50 p-4 border border-blue-200 rounded-lg">
                                      <div>
                                        <h4 className="font-semibold text-gray-900">{role.role}</h4>
                                        <p className="text-gray-600 text-sm">{role.reason}</p>
                                      </div>
                                      <div className="bg-blue-100 px-3 py-1 rounded-full font-bold text-blue-700">
                                        {role.match}%
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </Card>
                        )}

                        {/* Professional Summary */}
                        {result.professional_summary && (
                          <Card padding="xl">
                            <SectionHeader 
                              title="📈 Professional Summary" 
                              icon="fas fa-user-tie"
                              subtitle="Overall assessment and career recommendations"
                            />

                            <div className="space-y-6">
                              {/* Positioning Statement */}
                              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 border border-purple-200 rounded-xl">
                                <h3 className="flex items-center mb-3 font-semibold text-purple-700">
                                  <i className="mr-2 fas fa-star"></i>
                                  Who They Are
                                </h3>
                                <p className="text-gray-700 leading-relaxed">{result.professional_summary.positioning}</p>
                              </div>

                              <div className="gap-6 grid md:grid-cols-2">
                                {/* Strengths */}
                                <div className="bg-green-50 p-6 border border-green-200 rounded-xl">
                                  <h3 className="flex items-center mb-4 font-semibold text-green-700">
                                    <i className="mr-2 fas fa-thumbs-up"></i>
                                    Key Strengths
                                  </h3>
                                  <ul className="space-y-2">
                                    {result.professional_summary.strengths.map((strength: string, idx: number) => (
                                      <li key={idx} className="flex items-start">
                                        <i className="mt-1 mr-2 text-green-600 text-xs fas fa-check-circle"></i>
                                        <span className="text-gray-700 text-sm">{strength}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Growth Areas */}
                                <div className="bg-orange-50 p-6 border border-orange-200 rounded-xl">
                                  <h3 className="flex items-center mb-4 font-semibold text-orange-700">
                                    <i className="mr-2 fas fa-arrow-up"></i>
                                    Growth Areas
                                  </h3>
                                  <ul className="space-y-2">
                                    {result.professional_summary.growth_areas.map((area: string, idx: number) => (
                                      <li key={idx} className="flex items-start">
                                        <i className="mt-1 mr-2 text-orange-600 text-xs fas fa-exclamation-circle"></i>
                                        <span className="text-gray-700 text-sm">{area}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              {/* Career Trajectory */}
                              <div className="bg-blue-50 p-6 border border-blue-200 rounded-xl">
                                <h3 className="flex items-center mb-3 font-semibold text-blue-700">
                                  <i className="mr-2 fas fa-rocket"></i>
                                  Career Trajectory
                                </h3>
                                <p className="text-gray-700">{result.professional_summary.career_trajectory}</p>
                              </div>
                            </div>
                          </Card>
                        )}

                        {/* AI Insights */}
                        <Card padding="xl">
                          <SectionHeader 
                            title="🧠 AI Insights" 
                            icon="fas fa-brain"
                            subtitle="Comprehensive analysis and recommendations"
                          />
                          
                          <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 border border-purple-200 rounded-xl">
                            <p className="text-gray-700 leading-relaxed">{result.ai_summary}</p>
                          </div>
                        </Card>

                        {/* Action Buttons */}
                        <Card padding="lg">
                          <div className="flex justify-between items-center">
                            <div className="text-gray-500 text-sm">
                              Analysis completed on {new Date(result.analyzed_date).toLocaleDateString()}
                            </div>
                            
                            <div className="flex gap-3">
                              <Button variant="outline" size="sm">
                                <i className="mr-2 fas fa-download"></i>
                                Download Report
                              </Button>
                              <Button variant="outline" size="sm">
                                <i className="mr-2 fas fa-share"></i>
                                Share Analysis
                              </Button>
                              {selectedJob && (
                                <Button size="sm">
                                  <i className="mr-2 fas fa-user-plus"></i>
                                  Add to Pipeline
                                </Button>
                              )}
                            </div>
                          </div>
                        </Card>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Empty State */}
            {uploadedFiles.length === 0 && analysisResults.length === 0 && (
              <Card padding="xl">
                <div className="py-12 text-center">
                  <div className="inline-flex justify-center items-center bg-gradient-to-br from-blue-100 to-green-100 mx-auto mb-6 rounded-full w-20 h-20">
                    <i className="text-blue-600 text-3xl fas fa-user-circle"></i>
                  </div>
                  <h3 className="mb-2 font-semibold text-gray-900 text-xl">Discover Your CV Potential</h3>
                  <p className="mx-auto mb-6 max-w-md text-gray-500">
                    Upload your CV to get personalized insights about your skills, experience level, and career opportunities.
                  </p>
                  <div className="flex justify-center gap-4">
                    <Button onClick={() => fileInputRef.current?.click()}>
                      <i className="mr-2 fas fa-upload"></i>
                      Upload My CV
                    </Button>
                    <Link href="/jobs">
                      <Button variant="outline">
                        <i className="mr-2 fas fa-search"></i>
                        Browse Opportunities
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
