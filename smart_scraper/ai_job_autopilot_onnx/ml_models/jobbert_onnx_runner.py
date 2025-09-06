import onnxruntime as ort
import torch
from transformers import AutoTokenizer
import numpy as np

MODEL_PATH = "onnx_model/jobbert-v3.onnx"
TOKENIZER = AutoTokenizer.from_pretrained("TechWolf/JobBERT-v3")

sess = ort.InferenceSession(MODEL_PATH)

def embed(text):
    inputs = TOKENIZER(text, return_tensors="np", padding="max_length", truncation=True, max_length=256)
    ort_inputs = {k: v for k, v in inputs.items()}
    ort_outs = sess.run(None, ort_inputs)
    return ort_outs[0][0]

def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def match_resume_to_jobs(resume_text, jobs):
    resume_vec = embed(resume_text)
    matches = []

    for job in jobs:
        job_vec = embed(job["description"])
        score = round(cosine_similarity(resume_vec, job_vec) * 100, 2)
        matches.append({**job, "score": score})

    return sorted(matches, key=lambda x: -x["score"])