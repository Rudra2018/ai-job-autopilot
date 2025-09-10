
import React from 'react';

const jobs = [{"title": "Spezialist (m/w/d) Stammdatenmanagement \u2013 SAP S/4HANA", "company": null, "location": "Frankfurt", "salary_estimate": null, "job_url": "https://www.arbeitnow.com/jobs/companies/univativ-gmbh/spezialist-stammdatenmanagement-sap-s-4hana-frankfurt-99846", "apply_type": "External"}, {"title": "Senior Financial Controller (m/w/d)", "company": null, "location": "Darmstadt", "salary_estimate": null, "job_url": "https://www.arbeitnow.com/jobs/companies/univativ-gmbh/senior-financial-controller-darmstadt-65929", "apply_type": "External"}, {"title": "Wirtschaftspr\u00fcfer Audit & Advisory (m/w/d) bring deine Karriere ins Rollen", "company": null, "location": "Munich", "salary_estimate": null, "job_url": "https://www.arbeitnow.com/jobs/companies/schwertfels-consulting-gmbh/wirtschaftsprufer-audit-advisory-bring-deine-karriere-ins-rollen-munich-79605", "apply_type": "External"}, {"title": "Wirtschaftspr\u00fcfer Audit & Advisory (m/w/d) bring deine Karriere ins Rollen", "company": null, "location": "Frankfurt", "salary_estimate": null, "job_url": "https://www.arbeitnow.com/jobs/companies/schwertfels-consulting-gmbh/wirtschaftsprufer-audit-advisory-bring-deine-karriere-ins-rollen-frankfurt-431283", "apply_type": "External"}, {"title": "Desktop Support Specialist (m/w/d)", "company": null, "location": "Frankfurt", "salary_estimate": null, "job_url": "https://www.arbeitnow.com/jobs/companies/univativ-gmbh/desktop-support-specialist-frankfurt-92291", "apply_type": "External"}];

export default function Dashboard() {
  return (
    <div className='p-6 space-y-4'>
      <h1 className='text-3xl font-bold'>AI Job Autopilot</h1>
      <section>
        <h2 className='text-xl font-semibold'>Application Report</h2>
        <p>Applied Jobs: 5 / 5</p>
        <p>Success Rate: 100.0%</p>
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
    </div>
  );
}
