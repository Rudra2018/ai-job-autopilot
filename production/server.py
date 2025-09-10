from pathlib import Path
import json
from typing import Dict

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .main import run_pipeline

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG: Dict[str, any] = {}


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / file.filename
    file_path.write_bytes(await file.read())
    CONFIG["resume_path"] = str(file_path)
    return {"status": "uploaded", "path": str(file_path)}


@app.post("/preferences")
async def set_preferences(prefs: Dict[str, any]):
    CONFIG.setdefault("preferences", {}).update(prefs)
    return {"status": "ok"}


@app.post("/credentials")
async def set_credentials(creds: Dict[str, any]):
    CONFIG.update(creds)
    return {"status": "ok"}


@app.post("/run_pipeline")
async def run_pipeline_endpoint():
    dashboard = run_pipeline(CONFIG)
    Path("final_dashboard.json").write_text(json.dumps(dashboard, indent=2))
    return dashboard


@app.get("/final_dashboard.json")
async def get_dashboard():
    path = Path("final_dashboard.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"error": "dashboard not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("production.server:app", host="0.0.0.0", port=8000)
