import Link from "next/link";

export default function Homepage() {
  return (
    <main className="flex flex-col justify-center items-center bg-gradient-to-br from-purple-50 to-blue-50 min-h-screen">
      <div className="mx-auto py-20 w-full max-w-2xl text-center">
        <h1 className="mb-6 font-extrabold text-purple-700 text-5xl">AI-Powered HR Platform</h1>
        <p className="mb-8 text-gray-700 text-lg">Connect exceptional talent with innovative organizations. Let our agent help you create, analyze, and post jobs smarter and faster.</p>
        <div className="flex sm:flex-row flex-col justify-center gap-4">
          <Link href="/jobs">
            <button className="bg-blue-600 hover:bg-blue-700 shadow-lg px-8 py-4 rounded-2xl font-bold text-white text-xl transition">
              <i className="mr-2 fas fa-briefcase"></i>
              Explore Jobs
            </button>
          </Link>
          <Link href="/jobs/create">
            <button className="bg-purple-600 hover:bg-purple-700 shadow-lg px-8 py-4 rounded-2xl font-bold text-white text-xl transition">
              <i className="mr-2 fas fa-plus"></i>
              Create Job
            </button>
          </Link>
          <Link href="/cvs/analyze">
            <button className="bg-green-600 hover:bg-green-700 shadow-lg px-8 py-4 rounded-2xl font-bold text-white text-xl transition">
              <i className="mr-2 fas fa-brain"></i>
              Analyze CVs
            </button>
          </Link>
        </div>
      </div>
      <div className="space-y-8 mt-16">
        <div className="bg-white shadow-xl mx-auto p-8 rounded-2xl max-w-xl">
          <h2 className="mb-2 font-bold text-blue-700 text-2xl">
            <i className="mr-2 fas fa-robot"></i>
            Meet Your AI HR Agent
          </h2>
          <p className="text-gray-700">Our agent analyzes job descriptions, suggests requirements, and summarizes roles for you. Save time and hire smarter.</p>
        </div>
        
        <div className="bg-white shadow-xl mx-auto p-8 rounded-2xl max-w-xl">
          <h2 className="mb-2 font-bold text-green-700 text-2xl">
            <i className="mr-2 fas fa-search"></i>
            AI-Powered CV Analysis
          </h2>
          <p className="text-gray-700">Upload candidate CVs and get instant AI insights, skill extraction, job matching scores, and personalized recommendations.</p>
        </div>
      </div>
    </main>
  );
}
