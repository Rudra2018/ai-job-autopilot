import React, { useEffect, useState } from 'react'

export default function JobDashboard() {
  const [jobs, setJobs] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/final_dashboard.json')
      .then(r => r.json())
      .then(data => setJobs(data.job_matches || []))
      .catch(() => {})
  }, [])

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Job Matches</h2>
      <div className="grid gap-4 md:grid-cols-2">
        {jobs.map((job, idx) => (
          <div key={idx} className="p-4 border rounded shadow">
            <h3 className="font-semibold">{job.title || 'Job Title'}</h3>
            <p className="text-sm text-gray-600">{job.company || 'Company'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
