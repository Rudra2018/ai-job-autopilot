import { useState } from 'react';
import Dashboard from '../../generated/Dashboard';

export default function Home() {
  const [data, setData] = useState(null);

  const runPipeline = async () => {
    await fetch('/api/run-pipeline', { method: 'POST' }).catch(() => {});
    const res = await fetch('/api/dashboard');
    if (res.ok) {
      const json = await res.json();
      setData(json);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <button
        onClick={runPipeline}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Run Pipeline
      </button>
      {data && <Dashboard data={data} />}
    </div>
  );
}
