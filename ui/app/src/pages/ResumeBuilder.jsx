import React from 'react'

export default function ResumeBuilder() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Resume Builder</h2>
      <input type="file" className="border p-2" />
      <p className="text-gray-600">Upload a resume to begin.</p>
    </div>
  )
}
