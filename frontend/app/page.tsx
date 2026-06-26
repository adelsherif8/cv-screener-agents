"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Homepage() {
  const router = useRouter();
  const [showSignInModal, setShowSignInModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    router.push("/");
  };

  const handleJobsClick = () => {
    if (user) {
      router.push("/jobs");
    } else {
      router.push("/auth/login");
    }
  };

  const handleAddJobClick = () => {
    if (user) {
      router.push("/jobs/create");
    } else {
      router.push("/auth/login");
    }
  };

  return (
    <>
      <main className="relative bg-gradient-to-br from-purple-100 via-purple-50 to-pink-50 min-h-screen overflow-hidden">
        {/* Enhanced Background Elements with Animation */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="top-0 right-0 absolute bg-gradient-to-bl from-purple-200/30 via-purple-100/20 to-transparent w-full h-full animate-pulse"></div>
          <div className="bottom-0 left-0 absolute bg-gradient-to-tr from-pink-200/20 via-purple-100/10 to-transparent w-full h-full animate-pulse delay-1000"></div>
          <div className="top-1/4 left-1/4 absolute bg-gradient-to-br from-blue-300/20 to-purple-300/20 blur-3xl rounded-full w-96 h-96 animate-bounce slow-bounce"></div>
          <div className="right-1/3 bottom-1/3 absolute bg-gradient-to-br from-pink-300/20 to-indigo-300/20 blur-3xl rounded-full w-80 h-80 animate-pulse delay-500"></div>
        </div>
        
        {/* Top Navigation */}
        <nav className="z-10 relative flex justify-between items-center px-12 lg:px-20 py-8">
          <div className="flex items-center space-x-4">
            <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg rounded-xl w-12 h-12 animate-pulse">
              <span className="font-bold text-white text-lg">👥</span>
            </div>
            <span className="font-bold text-gray-900 text-3xl">HRAI</span>
            <span className="bg-purple-100 px-3 py-1 rounded-full font-medium text-purple-700 text-sm">AI Agent</span>
          </div>
          
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-4">
              <button className="hover:bg-white/50 p-3 rounded-xl hover:scale-110 transition-all duration-300">
                <span className="text-2xl">📊</span>
              </button>
              <button className="hover:bg-white/50 p-3 rounded-xl hover:scale-110 transition-all duration-300">
                <span className="text-2xl">🔔</span>
              </button>
              <button className="hover:bg-white/50 p-3 rounded-xl hover:scale-110 transition-all duration-300">
                <span className="text-2xl">⚙️</span>
              </button>
            </div>
            
            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user.full_name || user.username}!</span>
                <button 
                  onClick={handleLogout}
                  className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-xl font-semibold text-gray-700 transition-all duration-300"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link href="/auth/login">
                  <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg px-6 py-3 rounded-xl font-semibold text-white hover:scale-105 transition-all duration-300">
                    Sign In
                  </button>
                </Link>
                <Link href="/auth/register">
                  <button className="bg-white hover:bg-gray-50 px-6 py-3 border-2 border-purple-200 rounded-xl font-semibold text-purple-600 hover:scale-105 transition-all duration-300">
                    Sign Up
                  </button>
                </Link>
              </div>
            )}
          </div>
        </nav>
        
        <div className="z-10 relative flex lg:flex-row flex-col min-h-[calc(100vh-120px)]">
          {/* Left Section - Content */}
          <div className="flex flex-col flex-1 justify-center px-16 lg:px-32 py-20">
            <div className="max-w-5xl">
              {/* Logo Grid */}
              <div className="mb-20">
                <div className="gap-3 grid grid-cols-2 mb-16 w-32 h-32">
                  <div className="flex justify-center items-center bg-gradient-to-br from-purple-400 to-blue-400 border-4 border-purple-500 rounded-2xl text-white text-2xl animate-pulse">
                    👤
                  </div>
                  <div className="flex justify-center items-center bg-gradient-to-br from-blue-400 to-cyan-400 border-4 border-blue-500 rounded-2xl text-white text-2xl animate-pulse delay-300">
                    💼
                  </div>
                  <div className="flex justify-center items-center bg-gradient-to-br from-cyan-400 to-purple-400 border-4 border-cyan-500 rounded-2xl text-white text-2xl animate-pulse delay-600">
                    🤖
                  </div>
                  <div className="flex justify-center items-center bg-gradient-to-br from-purple-400 to-pink-400 border-4 border-purple-500 rounded-2xl text-white text-2xl animate-pulse delay-900">
                    ⚡
                  </div>
                </div>
              </div>

              {/* Main Heading */}
              <div className="space-y-10 mb-20">
                <h1 className="font-bold text-gray-900 text-8xl lg:text-9xl leading-[0.85]">
                  Experience the future
                  <br />
                  of <span className="bg-clip-text bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 text-transparent">HR with AI</span>
                </h1>
                <p className="max-w-4xl font-medium text-gray-600 text-2xl lg:text-3xl leading-relaxed">
                  Transform your recruitment process with our intelligent HR agent. 
                  Automate job postings, screen candidates, and optimize your hiring workflow.
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex space-x-6 mb-24">
                <button 
                  onClick={handleJobsClick}
                  className="group flex items-center space-x-4 bg-gradient-to-r from-purple-600 hover:from-purple-700 to-blue-600 hover:to-blue-700 shadow-2xl hover:shadow-3xl px-16 py-8 rounded-3xl font-bold text-white text-xl hover:scale-105 transition-all duration-300"
                >
                  <span className="text-2xl">💼</span>
                  <span>{user ? 'My Jobs' : 'View Jobs'}</span>
                  <div className="flex justify-center items-center bg-white rounded-full w-10 h-10 group-hover:rotate-12 transition-transform duration-300">
                    <span className="font-bold text-purple-600 text-xl">→</span>
                  </div>
                </button>
                <button 
                  onClick={handleAddJobClick}
                  className="group flex items-center space-x-4 bg-white hover:bg-gray-50 shadow-xl hover:shadow-2xl px-16 py-8 border-2 border-purple-200 rounded-3xl font-bold text-gray-900 text-xl hover:scale-105 transition-all duration-300"
                >
                  <span className="text-2xl">➕</span>
                  <span>Add Job</span>
                </button>
              </div>

              {/* Quote */}
              <div className="space-y-8">
                <p className="font-normal text-gray-900 text-5xl lg:text-6xl leading-relaxed">
                  "We <span className="text-gray-400">envision</span> a <span className="text-cyan-500">workplace</span> with <span className="text-purple-600">no limits</span>."
                </p>
                <div className="flex items-center space-x-8">
                  <div className="bg-gradient-to-r from-purple-400 to-blue-400 w-20 h-px"></div>
                  <p className="text-gray-500 text-xl">HRAI Team</p>
                </div>
              </div>

              {/* Trust Section */}
              <div className="mt-24">
                <div className="flex items-center space-x-8">
                  <div className="bg-gradient-to-r from-purple-400 to-cyan-400 w-24 h-px"></div>
                  <p className="max-w-lg text-gray-600 text-xl">Trusted by leading HR professionals and innovative companies worldwide</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Section - Enhanced Visual Content */}
          <div className="relative flex-1 px-16 lg:px-32 py-20">
            {/* Main AI Visual Background */}
            <div className="relative flex justify-center items-center h-full min-h-[700px]">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-300/50 via-blue-300/40 to-pink-300/50 backdrop-blur-sm rounded-3xl animate-pulse">
                {/* Enhanced 3D AI brain/network effect */}
                <div className="top-1/4 right-1/4 absolute bg-gradient-to-br from-purple-500/70 via-blue-500/70 to-pink-500/70 blur-2xl rounded-full w-60 h-60 animate-bounce"></div>
                <div className="bottom-1/4 left-1/4 absolute bg-gradient-to-br from-blue-500/60 via-purple-500/60 to-cyan-500/60 blur-2xl rounded-full w-72 h-72 animate-pulse delay-700"></div>
                <div className="top-1/2 left-1/2 absolute bg-gradient-to-br from-pink-500/50 via-purple-500/50 to-blue-500/50 blur-3xl rounded-full w-80 h-80 -translate-x-1/2 -translate-y-1/2 animate-pulse delay-1000 transform"></div>
                
                {/* AI Network Lines */}
                <div className="top-1/3 left-1/3 absolute bg-gradient-to-b from-purple-400 to-transparent rounded-full w-2 h-20 animate-pulse"></div>
                <div className="right-1/3 bottom-1/3 absolute bg-gradient-to-t from-blue-400 to-transparent rounded-full w-2 h-16 animate-pulse delay-500"></div>
                <div className="top-2/3 left-2/3 absolute bg-gradient-to-r from-cyan-400 to-transparent rounded-full w-20 h-2 animate-pulse delay-300"></div>
              </div>
              
              {/* HR Statistics Cards - Enhanced */}
              <div className="z-10 relative gap-8 grid grid-cols-2 mx-auto max-w-2xl">
                {/* Jobs Posted Card */}
                <button 
                  onClick={() => setShowStatsModal(true)}
                  className="group bg-white/95 shadow-2xl hover:shadow-3xl backdrop-blur-lg p-10 rounded-3xl hover:scale-105 transition-all hover:-translate-y-2 duration-300 cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-3xl group-hover:animate-spin">💼</span>
                    <div className="font-medium text-gray-500 text-sm">jobs posted daily</div>
                  </div>
                  <div className="font-bold text-gray-900 group-hover:text-purple-600 text-6xl transition-colors">500+</div>
                </button>
                
                {/* Candidates Matched Card */}
                <button 
                  onClick={() => setShowStatsModal(true)}
                  className="group bg-white/95 shadow-2xl hover:shadow-3xl backdrop-blur-lg p-10 rounded-3xl hover:scale-105 transition-all hover:-translate-y-2 duration-300 cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-3xl group-hover:animate-bounce">🎯</span>
                    <div className="font-medium text-gray-500 text-sm">candidates matched</div>
                  </div>
                  <div className="font-bold text-gray-900 group-hover:text-blue-600 text-6xl transition-colors">2.5M+</div>
                </button>
                
                {/* AI Accuracy Card */}
                <button 
                  onClick={() => setShowStatsModal(true)}
                  className="group bg-white/95 shadow-2xl hover:shadow-3xl backdrop-blur-lg p-10 rounded-3xl hover:scale-105 transition-all hover:-translate-y-2 duration-300 cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-3xl group-hover:animate-pulse">🤖</span>
                    <div className="font-medium text-gray-500 text-sm">AI accuracy rate</div>
                  </div>
                  <div className="font-bold text-gray-900 group-hover:text-cyan-600 text-6xl transition-colors">95%</div>
                </button>
                
                {/* Time Saved Card */}
                <button 
                  onClick={() => setShowStatsModal(true)}
                  className="group bg-white/95 shadow-2xl hover:shadow-3xl backdrop-blur-lg p-10 rounded-3xl hover:scale-105 transition-all hover:-translate-y-2 duration-300 cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-3xl group-hover:animate-spin">⚡</span>
                    <div className="font-medium text-gray-500 text-sm">time saved on hiring</div>
                  </div>
                  <div className="font-bold text-gray-900 group-hover:text-pink-600 text-6xl transition-colors">80%</div>
                </button>
              </div>
            </div>

            {/* HR Community Card - Enhanced */}
            <div className="top-12 right-12 absolute bg-white/95 shadow-2xl hover:shadow-3xl backdrop-blur-lg p-10 rounded-3xl max-w-md hover:scale-105 transition-all duration-300">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-3xl animate-bounce">👥</span>
                <h3 className="font-bold text-gray-900 text-2xl">Join HR Community</h3>
              </div>
              <p className="mb-6 text-gray-600 text-lg leading-relaxed">
                Connect with 10,000+ HR professionals using our AI agent for smarter recruitment
              </p>
              <div className="flex space-x-4 mb-4">
                <div className="flex justify-center items-center bg-gradient-to-br from-purple-400 to-blue-400 rounded-full w-12 h-12 font-bold text-white">
                  👤
                </div>
                <div className="flex justify-center items-center bg-gradient-to-br from-blue-400 to-cyan-400 rounded-full w-12 h-12 font-bold text-white">
                  👤
                </div>
                <div className="flex justify-center items-center bg-gradient-to-br from-cyan-400 to-purple-400 rounded-full w-12 h-12 font-bold text-white">
                  👤
                </div>
                <div className="flex justify-center items-center bg-gray-200 rounded-full w-12 h-12 font-bold text-gray-500">
                  +7K
                </div>
              </div>
              <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg py-3 rounded-xl w-full font-semibold text-white hover:scale-105 transition-all duration-300">
                Join Now
              </button>
            </div>

            {/* HR Feature Cards - Enhanced */}
            <div className="right-12 bottom-12 left-12 absolute space-y-6">
              <div className="flex space-x-6">
                <div className="flex-1 bg-white/95 shadow-xl hover:shadow-2xl backdrop-blur-lg p-8 rounded-2xl hover:scale-105 transition-all duration-300">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl w-16 h-16 text-3xl animate-pulse">
                      📋
                    </div>
                    <span className="font-bold text-gray-900 text-xl">Smart Screening</span>
                  </div>
                  <p className="text-gray-600">AI-powered candidate screening that analyzes resumes and matches skills automatically</p>
                </div>
                
                <div className="flex-1 bg-white/95 shadow-xl hover:shadow-2xl backdrop-blur-lg p-8 rounded-2xl hover:scale-105 transition-all duration-300">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="flex justify-center items-center bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl w-16 h-16 text-3xl animate-bounce">
                      📊
                    </div>
                    <span className="font-bold text-gray-900 text-xl">Analytics Dashboard</span>
                  </div>
                  <p className="text-gray-600">Comprehensive recruitment analytics with real-time insights and performance metrics</p>
                </div>
              </div>
              
              <div className="bg-white/95 shadow-xl hover:shadow-2xl backdrop-blur-lg p-8 rounded-2xl hover:scale-105 transition-all duration-300">
                <div className="flex items-start space-x-6">
                  <div className="flex justify-center items-center bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl w-20 h-20 text-4xl animate-spin slow-spin">
                    🧠
                  </div>
                  <div className="flex-1">
                    <h4 className="mb-3 font-bold text-gray-900 text-xl">AI-Powered Job Matching</h4>
                    <p className="text-gray-600 text-lg">Advanced machine learning algorithms that understand job requirements and candidate profiles for perfect matches</p>
                  </div>
                  <button className="flex justify-center items-center bg-gradient-to-r from-purple-600 to-blue-600 rounded-full w-12 h-12 hover:scale-110 transition-all duration-300">
                    <span className="text-white text-xl">→</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Sign In Modal */}
      {showSignInModal && (
        <div className="z-50 fixed inset-0 flex justify-center items-center bg-black/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white shadow-3xl mx-4 p-12 rounded-3xl max-w-md animate-slide-up">
            <div className="mb-8 text-center">
              <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-blue-500 mx-auto mb-6 rounded-2xl w-20 h-20">
                <span className="text-white text-3xl">👥</span>
              </div>
              <h2 className="mb-2 font-bold text-gray-900 text-3xl">Welcome to HRAI</h2>
              <p className="text-gray-600">Sign in to access your AI-powered HR dashboard</p>
            </div>
            
            <div className="space-y-4 mb-8">
              <input 
                type="email" 
                placeholder="Email address"
                className="p-4 border border-gray-300 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full transition-all duration-300"
              />
              <input 
                type="password" 
                placeholder="Password"
                className="p-4 border border-gray-300 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full transition-all duration-300"
              />
            </div>
            
            <div className="space-y-4">
              <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg py-4 rounded-xl w-full font-semibold text-white hover:scale-105 transition-all duration-300">
                Sign In
              </button>
              <button 
                onClick={() => setShowSignInModal(false)}
                className="hover:bg-gray-50 py-4 border border-gray-300 rounded-xl w-full font-semibold text-gray-700 transition-all duration-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Statistics Detail Modal */}
      {showStatsModal && (
        <div className="z-50 fixed inset-0 flex justify-center items-center bg-black/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white shadow-3xl mx-4 p-12 rounded-3xl max-w-2xl animate-slide-up">
            <div className="mb-8 text-center">
              <div className="flex justify-center items-center bg-gradient-to-br from-purple-500 to-blue-500 mx-auto mb-6 rounded-2xl w-24 h-24">
                <span className="text-white text-4xl">📊</span>
              </div>
              <h2 className="mb-4 font-bold text-gray-900 text-4xl">HRAI Performance</h2>
              <p className="text-gray-600 text-xl">Real-time statistics from our AI-powered HR platform</p>
            </div>
            
            <div className="gap-6 grid grid-cols-2 mb-8">
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-2xl">
                <div className="mb-2 text-4xl">💼</div>
                <div className="font-bold text-gray-900 text-2xl">500+</div>
                <div className="text-gray-600">Jobs posted daily</div>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-2xl">
                <div className="mb-2 text-4xl">🎯</div>
                <div className="font-bold text-gray-900 text-2xl">2.5M+</div>
                <div className="text-gray-600">Candidates matched</div>
              </div>
              <div className="bg-gradient-to-br from-cyan-50 to-purple-50 p-6 rounded-2xl">
                <div className="mb-2 text-4xl">🤖</div>
                <div className="font-bold text-gray-900 text-2xl">95%</div>
                <div className="text-gray-600">AI accuracy rate</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl">
                <div className="mb-2 text-4xl">⚡</div>
                <div className="font-bold text-gray-900 text-2xl">80%</div>
                <div className="text-gray-600">Time saved</div>
              </div>
            </div>
            
            <button 
              onClick={() => setShowStatsModal(false)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg py-4 rounded-xl w-full font-semibold text-white hover:scale-105 transition-all duration-300"
            >
              Close
            </button>
          </div>
        </div>
      )}

      <style jsx global>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        @keyframes slow-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
        .animate-slide-up { animation: slide-up 0.3s ease-out; }
        .animate-fade-in-delayed { animation: fade-in 0.6s ease-out; }
        .animate-gradient { background-size: 200% 200%; animation: gradient 3s ease infinite; }
        .slow-spin { animation: slow-spin 8s linear infinite; }
        .slow-bounce { animation: bounce 3s ease-in-out infinite; }
        .shadow-3xl { box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
      `}</style>
    </>
  );
}
