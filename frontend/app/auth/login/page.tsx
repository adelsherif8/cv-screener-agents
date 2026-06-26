"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface LoginForm {
  email: string;
  password: string;
}

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  company_name?: string;
  job_title?: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState<LoginForm>({
    email: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (response.ok) {
        const data: LoginResponse = await response.json();
        
        // Store token and user info in localStorage
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        
        // Redirect to jobs page
        router.push("/jobs");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center bg-gradient-to-br from-purple-100 via-blue-100 to-pink-100 px-4 min-h-screen">
      <div className="bg-white/80 shadow-2xl backdrop-blur-md p-8 rounded-3xl w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="flex justify-center items-center bg-gradient-to-r from-purple-600 to-blue-600 mx-auto mb-4 rounded-2xl w-16 h-16">
            <span className="text-white text-2xl">🚀</span>
          </div>
          <h1 className="mb-2 font-bold text-gray-900 text-3xl">Welcome Back</h1>
          <p className="text-gray-600">Sign in to manage your job postings</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block mb-2 font-medium text-gray-700 text-sm">
              Email Address
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="px-4 py-3 border border-gray-300 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full transition-all"
              placeholder="you@company.com"
              required
            />
          </div>

          <div>
            <label className="block mb-2 font-medium text-gray-700 text-sm">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="px-4 py-3 border border-gray-300 focus:border-transparent rounded-xl focus:ring-2 focus:ring-purple-500 w-full transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 p-4 border border-red-200 rounded-xl">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="bg-gradient-to-r from-purple-600 hover:from-purple-700 to-blue-600 hover:to-blue-700 disabled:opacity-50 px-4 py-3 rounded-xl w-full font-semibold text-white transition-all duration-300"
          >
            {loading ? (
              <span className="flex justify-center items-center">
                <svg className="mr-3 -ml-1 w-5 h-5 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing in...
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{" "}
            <Link href="/auth/register" className="font-medium text-purple-600 hover:text-purple-700">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
