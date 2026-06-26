"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  AppHeader, PageContainer, MainContent, Card, Button, SectionHeader, LoadingSpinner, ErrorDisplay 
} from "@/components/shared";

export default function CVsPage() {
  const [cvs, setCvs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Load analyzed CVs
  const loadCVs = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://127.0.0.1:8000/users/me/analyzed-cvs", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setCvs(data);
      }
    } catch (error) {
      console.error("Failed to load CVs:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCVs();
  }, []);

  const getMatchColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getMatchLabel = (score: number) => {
    if (score >= 80) return 'High Match';
    if (score >= 60) return 'Medium Match';
    return 'Low Match';
  };

  const filteredCVs = cvs.filter(cv => {
    const matchesSearch = cv.candidate_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cv.fileName?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (!matchesSearch) return false;
    
    if (filter === 'all') return true;
    if (filter === 'high') return cv.match_score >= 80;
    if (filter === 'medium') return cv.match_score >= 60 && cv.match_score < 80;
    if (filter === 'low') return cv.match_score < 60;
    
    return true;
  });

  if (loading) {
    return (
      <PageContainer>
        <AppHeader title="CV Database" subtitle="Manage analyzed CVs" />
        <MainContent>
          <div className="flex justify-center items-center py-20">
            <LoadingSpinner size="lg" />
          </div>
        </MainContent>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <AppHeader 
        title="CV Analysis Hub"
        subtitle="Professional CV analysis tools for users and HR teams"
        actions={
          <div className="flex space-x-3">
            <Link href="/cvs/analyze">
              <Button variant="primary">
                <i className="mr-2 fas fa-user-circle"></i>
                Personal CV Analysis
              </Button>
            </Link>
            <Link href="/jobs">
              <Button variant="outline">
                <i className="mr-2 fas fa-building"></i>
                HR: Job-Specific Analysis
              </Button>
            </Link>
          </div>
        }
      />

      <MainContent>
        {/* Tool Selection Cards */}
        <div className="gap-6 grid md:grid-cols-2 mb-8">
          {/* Personal Analysis Tool */}
          <Card padding="xl" hover className="group">
            <Link href="/cvs/analyze" className="block">
              <div className="text-center">
                <div className="flex justify-center items-center bg-gradient-to-br from-blue-100 to-green-100 mx-auto mb-4 rounded-full w-16 h-16 group-hover:scale-110 transition-transform">
                  <i className="text-blue-600 text-2xl fas fa-user-circle"></i>
                </div>
                <h3 className="mb-2 font-bold text-gray-900 group-hover:text-blue-600 text-xl transition-colors">
                  Personal CV Analysis
                </h3>
                <p className="mb-4 text-gray-600 text-sm">
                  For job seekers and professionals to analyze their own CVs, understand their skills, and improve their profiles.
                </p>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="font-medium text-blue-700 text-sm">
                    ✨ Perfect for: Career planning, skill assessment, CV improvement
                  </p>
                </div>
              </div>
            </Link>
          </Card>

          {/* HR Analysis Tool */}
          <Card padding="xl" hover className="group">
            <Link href="/jobs" className="block">
              <div className="text-center">
                <div className="flex justify-center items-center bg-gradient-to-br from-purple-100 to-indigo-100 mx-auto mb-4 rounded-full w-16 h-16 group-hover:scale-110 transition-transform">
                  <i className="text-purple-600 text-2xl fas fa-building"></i>
                </div>
                <h3 className="mb-2 font-bold text-gray-900 group-hover:text-purple-600 text-xl transition-colors">
                  HR: Job-Specific Analysis
                </h3>
                <p className="mb-4 text-gray-600 text-sm">
                  For HR professionals to evaluate candidates against specific job requirements with hiring recommendations.
                </p>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <p className="font-medium text-purple-700 text-sm">
                    🏢 Perfect for: Candidate evaluation, hiring decisions, requirement matching
                  </p>
                </div>
              </div>
            </Link>
          </Card>
        </div>

        {/* CV Database Section */}
        <div className="mb-6">
          <SectionHeader 
            title="📋 CV Database" 
            subtitle="Previously analyzed CVs and candidate profiles"
          />
        </div>

        <div className="gap-8 grid lg:grid-cols-4">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <Card padding="lg" className="top-4 sticky">
              <SectionHeader 
                title="Filters" 
                icon="fas fa-filter"
                size="sm"
              />
              
              <div className="space-y-4">
                {/* Search */}
                <div>
                  <label className="block mb-2 font-medium text-gray-700 text-sm">Search</label>
                  <div className="relative">
                    <i className="top-1/2 left-3 absolute text-gray-400 -translate-y-1/2 fas fa-search"></i>
                    <input
                      type="text"
                      placeholder="Search candidates..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="bg-white shadow py-2 pr-3 pl-10 border border-gray-300 focus:border-purple-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 w-full text-sm"
                    />
                  </div>
                </div>

                {/* Match Score Filter */}
                <div>
                  <label className="block mb-2 font-medium text-gray-700 text-sm">Match Score</label>
                  <div className="space-y-2">
                    {[
                      { value: 'all', label: 'All Candidates', count: cvs.length },
                      { value: 'high', label: 'High Match (80%+)', count: cvs.filter(cv => cv.match_score >= 80).length },
                      { value: 'medium', label: 'Medium Match (60-79%)', count: cvs.filter(cv => cv.match_score >= 60 && cv.match_score < 80).length },
                      { value: 'low', label: 'Low Match (<60%)', count: cvs.filter(cv => cv.match_score < 60).length }
                    ].map(option => (
                      <label key={option.value} className="flex justify-between items-center cursor-pointer">
                        <div className="flex items-center">
                          <input 
                            type="radio" 
                            name="filter" 
                            value={option.value}
                            checked={filter === option.value}
                            onChange={(e) => setFilter(e.target.value as any)}
                            className="mr-2 text-purple-600"
                          />
                          <span className="text-sm">{option.label}</span>
                        </div>
                        <span className="bg-gray-100 px-2 py-1 rounded text-gray-600 text-xs">
                          {option.count}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="pt-4 border-t">
                  <Link href="/cvs/analyze">
                    <Button className="w-full" size="sm">
                      <i className="mr-2 fas fa-plus"></i>
                      Analyze New CVs
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </div>

          {/* CVs List */}
          <div className="space-y-6 lg:col-span-3">
            {/* Header */}
            <Card padding="lg">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="font-bold text-gray-900 text-xl">
                    <i className="mr-3 text-blue-600 fas fa-users"></i>
                    Analyzed CVs
                  </h2>
                  <p className="text-gray-600">
                    {filteredCVs.length} candidate{filteredCVs.length !== 1 ? 's' : ''} found
                  </p>
                </div>
                
                <div className="flex gap-3">
                  <Button variant="outline" size="sm">
                    <i className="mr-2 fas fa-download"></i>
                    Export All
                  </Button>
                  <Link href="/cvs/analyze">
                    <Button size="sm">
                      <i className="mr-2 fas fa-brain"></i>
                      Analyze CVs
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>

            {/* CVs Grid */}
            {filteredCVs.length > 0 ? (
              <div className="gap-6 grid">
                {filteredCVs.map((cv, index) => (
                  <Card key={index} padding="lg" className="hover:shadow-lg transition-shadow">
                    <div className="flex justify-between items-start">
                      {/* Candidate Info */}
                      <div className="flex flex-1 items-start space-x-4">
                        <div className="flex justify-center items-center bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl w-12 h-12">
                          <i className="text-white fas fa-user"></i>
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <div>
                              <h3 className="font-semibold text-gray-900 text-lg">
                                {cv.candidate_name || 'Unknown Candidate'}
                              </h3>
                              <p className="text-gray-500 text-sm">{cv.fileName}</p>
                              {cv.position && (
                                <p className="mt-1 text-gray-600 text-sm">
                                  <i className="mr-1 text-purple-600 fas fa-briefcase"></i>
                                  {cv.position}
                                </p>
                              )}
                            </div>
                            
                            {cv.match_score && (
                              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchColor(cv.match_score)}`}>
                                {cv.match_score}%
                              </div>
                            )}
                          </div>

                          {/* Skills Preview */}
                          {cv.extracted_skills && cv.extracted_skills.length > 0 && (
                            <div className="mt-3">
                              <p className="mb-2 font-medium text-gray-700 text-sm">Top Skills:</p>
                              <div className="flex flex-wrap gap-1">
                                {cv.extracted_skills.slice(0, 5).map((skill: string, skillIndex: number) => (
                                  <span key={skillIndex} className="bg-blue-100 px-2 py-1 rounded text-blue-800 text-xs">
                                    {skill}
                                  </span>
                                ))}
                                {cv.extracted_skills.length > 5 && (
                                  <span className="text-gray-500 text-xs">
                                    +{cv.extracted_skills.length - 5} more
                                  </span>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Experience */}
                          {cv.experience_years && (
                            <div className="mt-2">
                              <span className="text-gray-600 text-sm">
                                <i className="mr-1 text-green-600 fas fa-calendar"></i>
                                {cv.experience_years} years experience
                              </span>
                            </div>
                          )}

                          {/* AI Insights Preview */}
                          {cv.ai_summary && (
                            <div className="mt-3">
                              <p className="text-gray-600 text-sm line-clamp-2">
                                <i className="mr-1 text-yellow-600 fas fa-lightbulb"></i>
                                {cv.ai_summary.substring(0, 120)}...
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-between items-center mt-4 pt-4 border-t">
                      <div className="text-gray-500 text-sm">
                        Analyzed {cv.analyzed_date ? new Date(cv.analyzed_date).toLocaleDateString() : 'Recently'}
                      </div>
                      
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <i className="mr-1 fas fa-eye"></i>
                          View
                        </Button>
                        <Button variant="outline" size="sm">
                          <i className="mr-1 fas fa-download"></i>
                          Report
                        </Button>
                        <Button size="sm">
                          <i className="mr-1 fas fa-user-plus"></i>
                          Interview
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              /* Empty State */
              <Card padding="xl">
                <div className="py-12 text-center">
                  <div className="inline-flex justify-center items-center bg-gray-100 mx-auto mb-6 rounded-full w-20 h-20">
                    <i className="text-gray-400 text-3xl fas fa-search"></i>
                  </div>
                  <h3 className="mb-2 font-semibold text-gray-900 text-xl">
                    {searchTerm || filter !== 'all' ? 'No CVs found' : 'No CVs analyzed yet'}
                  </h3>
                  <p className="mx-auto mb-6 max-w-md text-gray-500">
                    {searchTerm || filter !== 'all' 
                      ? 'Try adjusting your search or filter criteria.'
                      : 'Start by analyzing some candidate CVs to see them here.'
                    }
                  </p>
                  <div className="flex justify-center gap-4">
                    {searchTerm || filter !== 'all' ? (
                      <Button onClick={() => { setSearchTerm(''); setFilter('all'); }}>
                        <i className="mr-2 fas fa-times"></i>
                        Clear Filters
                      </Button>
                    ) : (
                      <Link href="/cvs/analyze">
                        <Button>
                          <i className="mr-2 fas fa-brain"></i>
                          Analyze First CV
                        </Button>
                      </Link>
                    )}
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
