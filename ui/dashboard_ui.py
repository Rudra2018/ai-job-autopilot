import streamlit as st
from worker.keyword_matcher import match_jobs_to_resume
from worker.recruiter_message_generator import generate_message
from extensions.mock_interview import ask_question
from worker.playwright_apply import (
    auto_detect_and_apply,
    set_platform_credentials,
    smart_apply,
    upload_and_parse_resume,
)
from worker.application_logger import read_application_log
from pathlib import Path

st.set_page_config(page_title="AI Job Autopilot", layout="wide")
st.title("🧠 AI Job Autopilot Dashboard")

st.sidebar.header("Upload Resume")
resume_file = st.sidebar.file_uploader(
    "Choose your resume (PDF or DOCX)", type=["pdf", "docx"]
)
resume_text = ""

if resume_file:
    temp_path = Path("temp_resume." + resume_file.name.split(".")[-1])
    with open(temp_path, "wb") as f:
        f.write(resume_file.read())
    resume_data = upload_and_parse_resume(temp_path)
    resume_text = resume_data.get("text", "")
    st.subheader("📄 Resume Preview")
    st.code(resume_text[:3000], language="text")

st.sidebar.header("Credentials")
li_email = st.sidebar.text_input("LinkedIn Email")
li_password = st.sidebar.text_input("LinkedIn Password", type="password")
xing_email = st.sidebar.text_input("Xing Email")
xing_password = st.sidebar.text_input("Xing Password", type="password")
if li_email and li_password:
    set_platform_credentials("linkedin", li_email, li_password)
if xing_email and xing_password:
    set_platform_credentials("xing", xing_email, xing_password)

if resume_text:
    st.markdown("### 🎯 Match to Target Jobs")
    matched_jobs = match_jobs_to_resume(
        resume_text,
        ["Security Engineer", "Cloud Security Engineer"],
        {"locations": ["Berlin", "Remote"]},
    )
    for idx, job in enumerate(matched_jobs):
        st.success(f"Matched: {job['title']} at {job['company']}")
        if st.button(
            f"Auto Apply: {job['title']} @ {job['company']}",
            key=f"apply_{idx}",
        ):
            with st.spinner("Applying via Easy Apply..."):
                auto_detect_and_apply(job)

    if st.button("AI Smart Apply to All Matches"):
        with st.spinner("Scanning and applying to jobs..."):
            smart_apply(resume_path=temp_path)

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
