import streamlit as st
from extensions.parser import parse_resume
from worker.keyword_matcher import match_jobs_to_resume
from worker.recruiter_message_generator import generate_message
from extensions.mock_interview import ask_question
from worker.playwright_apply import simulate_job_apply
from worker.application_logger import read_application_log
from pathlib import Path

st.set_page_config(page_title="AI Job Autopilot", layout="wide")
st.title("🧠 AI Job Autopilot Dashboard")

st.sidebar.header("Upload Resume")
resume_file = st.sidebar.file_uploader("Choose your resume (PDF or DOCX)", type=["pdf", "docx"])
resume_text = ""

if resume_file:
    temp_path = Path("temp_resume." + resume_file.name.split('.')[-1])
    with open(temp_path, "wb") as f:
        f.write(resume_file.read())
    resume_text = parse_resume(temp_path)
    st.subheader("📄 Resume Preview")
    st.code(resume_text[:3000], language="text")

if resume_text:
    st.markdown("### 🎯 Match to Target Jobs")
    matched_jobs = match_jobs_to_resume(resume_text, ["Security Engineer", "Cloud Security Engineer"], {"locations": ["Berlin", "Remote"]})
    for job in matched_jobs:
        st.success(f"Matched: {job['title']} at {job['company']}")
        if st.button(f"Auto Apply: {job['title']} @ {job['company']}"):
            simulate_job_apply(job)

    st.markdown("---")
    st.markdown("### 💬 Mock Interview")
    user_q = st.text_input("Ask interview question")
    if user_q:
        response = ask_question(user_q)
        st.info(f"🤖 {response}")

    st.markdown("---")
    st.markdown("### 🧑‍💼 Recruiter Message Generator")
    if st.button("Generate Outreach Message"):
        demo_job = {"title": "Security Engineer", "location": "Berlin"}
        msg = generate_message("Candidate", demo_job, tone="formal")
        st.code(msg, language="text")

# Display application log
st.markdown("---")
st.markdown("### 📊 Application Log")
log_entries = read_application_log()
if log_entries:
    st.table(log_entries)
else:
    st.info("No applications recorded yet.")
