"use client";

import { useEffect, useState } from "react";

interface Job {
  job_id: string;
  media_url: string;
  triage_result: string;
  approval_status: string;
  is_diy: boolean;
  estimated_cost: number;
  category?: string;
  invoice_amount?: number;
  vendor_notes?: string;
  post_repair_media_url?: string;
  bids?: string;
  ai_diagnosis?: string;
  clerk_note?: string;
  store_id?: string;
  asset_id?: string;
  qa_notes?: string;
}

export default function OwnerDashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [diagnosingId, setDiagnosingId] = useState<string | null>(null);
  const [uploadingJobId, setUploadingJobId] = useState<string | null>(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch("http://localhost:8000/jobs");
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (error) {
      console.error("Failed to fetch jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (jobId: string, status: string) => {
    try {
      await fetch(`http://localhost:8000/jobs/${jobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
      });
      // Refresh the list immediately
      fetchJobs();
    } catch (error) {
      console.error("Failed to update status:", error);
    }
  };

  const requestAIDiagnosis = async (jobId: string) => {
    try {
      setDiagnosingId(jobId);
      await fetch(`http://localhost:8000/jobs/${jobId}/ai-diagnose`, {
        method: "POST"
      });
      fetchJobs();
    } catch (error) {
      console.error("Failed to fetch AI diagnosis:", error);
    } finally {
      setDiagnosingId(null);
    }
  };

  const requestQA = async (jobId: string, url: string) => {
    setUploadingJobId(jobId);
    try {
      await fetch(`http://localhost:8000/jobs/${jobId}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_repair_media_url: url })
      });
      await fetchJobs();
    } catch (err) {
      console.error("Failed to request QA:", err);
    } finally {
      setUploadingJobId(null);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading jobs...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Owner Dashboard</h1>
        
        {jobs.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
            No maintenance jobs found.
          </div>
        ) : (
          <div className="space-y-6">
            {jobs.map((job) => (
              <div key={job.job_id} className="bg-white rounded-lg shadow overflow-hidden flex flex-col md:flex-row">
                {/* Image Section */}
                <div className="md:w-1/3 bg-gray-100 flex flex-col items-center p-4 border-r border-gray-200">
                  <span className="text-xs font-bold text-gray-400 tracking-widest mb-2 uppercase">Original Issue</span>
                  {/* Convert S3 localstack URL to localhost so the browser can load it */}
                  <img 
                    src={job.media_url.replace("localstack", "localhost")} 
                    alt="Maintenance Issue" 
                    className="w-full max-h-48 object-cover rounded shadow mb-4"
                    onError={(e) => (e.currentTarget.src = 'https://via.placeholder.com/300?text=No+Image')}
                  />
                  
                  {job.post_repair_media_url && (
                    <div className="mt-4 w-full flex flex-col items-center">
                        <span className="text-xs font-bold text-gray-400 tracking-widest mb-2 uppercase">Repaired State</span>
