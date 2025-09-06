from difflib import SequenceMatcher

def jobbert_score(resume_text, job_desc):
    return round(SequenceMatcher(None, resume_text.lower(), job_desc.lower()).ratio() * 100, 2)