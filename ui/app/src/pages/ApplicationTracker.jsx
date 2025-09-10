import React from 'react'

export default function ApplicationTracker() {
  const columns = ['Applied', 'Interview', 'Offer']
  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Application Tracker</h2>
      <div className="grid grid-cols-3 gap-4">
        {columns.map(col => (
          <div key={col} className="border rounded p-2">
            <h3 className="font-semibold mb-2">{col}</h3>
            <div className="text-sm text-gray-500">No items</div>
          </div>
        ))}
      </div>
    </div>
  )
}
