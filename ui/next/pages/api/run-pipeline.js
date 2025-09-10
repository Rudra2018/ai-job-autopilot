export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).end();
    return;
  }
  try {
    await fetch('http://localhost:8000/run-pipeline', { method: 'POST' });
  } catch (e) {
    // ignore backend errors
  }
  res.status(200).json({ status: 'triggered' });
}
