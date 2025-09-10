import React, { useState } from 'react'
import ResumeBuilder from './pages/ResumeBuilder'
import JobDashboard from './pages/JobDashboard'
import CoverLetterEditor from './pages/CoverLetterEditor'
import ApplicationTracker from './pages/ApplicationTracker'
import OptimizationInsights from './pages/OptimizationInsights'

const PAGES = {
  resume: <ResumeBuilder />,
  dashboard: <JobDashboard />,
  cover: <CoverLetterEditor />,
  tracker: <ApplicationTracker />,
  optimize: <OptimizationInsights />,
}

export default function App() {
  const [page, setPage] = useState('resume')
  return (
    <div className="min-h-screen">
      <nav className="bg-blue-600 text-white p-4 flex gap-4">
        <button onClick={() => setPage('resume')}>Resume Builder</button>
        <button onClick={() => setPage('dashboard')}>Job Dashboard</button>
        <button onClick={() => setPage('cover')}>Cover Letters</button>
        <button onClick={() => setPage('tracker')}>Tracker</button>
        <button onClick={() => setPage('optimize')}>Optimization</button>
      </nav>
      <main className="p-4">
        {PAGES[page]}
      </main>
    </div>
  )
}
