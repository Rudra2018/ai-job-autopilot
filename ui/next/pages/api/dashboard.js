export default async function handler(req, res) {
  try {
    const r = await fetch('http://localhost:8000/final_dashboard.json');
    const json = await r.json();
    res.status(200).json(json);
  } catch (e) {
    res.status(500).json({ error: 'backend unreachable' });
  }
}
