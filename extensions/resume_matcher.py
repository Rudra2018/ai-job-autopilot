from ml_models.jobbert_ranker import score_resume_job
from extensions.llm_vertex import call_vertex_flash_if_available
from yaml import safe_load

def match_jobs_to_resume(resume_text, user_profile_path="config/user_profile.yaml"):
    with open(user_profile_path, "r") as f:
        profile = safe_load(f)

    matched_jobs = []
    for job in profile.get("job_targets", []):
        job_desc = f"{job['title']} in {job['location']}"
        score1 = score_resume_job(resume_text, job_desc)
        try:
            gemini_score = call_vertex_flash_if_available(
                f"What is the match score (0-100) between this resume and this role:\n\nResume:\n{resume_text[:3000]}\n\nJob:\n{job_desc}\n\nReturn only a number."
            )
            score2 = float(gemini_score.strip().split()[0])
        except:
            score2 = 0

        final_score = round((score1 + score2) / 2, 2)
        matched_jobs.append({**job, "match_score": final_score})

    matched_jobs = [j for j in matched_jobs if j["match_score"] > 60]
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_jobs

