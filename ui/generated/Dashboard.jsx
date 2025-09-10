
import React from 'react';


export default function Dashboard({ data }) {
  const jobs = data.job_posts_json || [];
  const report = data.application_report_json || {};
  return (
    <div className='p-6 space-y-4'>
      <h1 className='text-3xl font-bold'>AI Job Autopilot</h1>
      <section>
        <h2 className='text-xl font-semibold'>Application Report</h2>
        <p>Applied Jobs: {report.applied_count} / {report.total_jobs}</p>
        <p>Success Rate: {report.success_rate}%</p>
      </section>
      <section>
        <h2 className='text-xl font-semibold'>Latest Jobs</h2>
        <ul className='space-y-2'>
          {jobs.map((job) => (
            <li key={job.job_url} className='border p-3 rounded hover:bg-gray-50'>
              <a href={job.job_url} target='_blank' rel='noopener noreferrer' className='font-medium text-blue-600'>{job.title}</a>
              <p className='text-sm text-gray-600'>{job.company} - {job.location}</p>
            </li>
          ))}
        </ul>
      </section>
=======
export default function Dashboard() {
  return (
    <div className='p-4'>
      <h1 className='text-2xl font-bold'>AI Job Autopilot</h1>
      <p>Applied Jobs: 0 / 5</p>

    </div>
  );
}
