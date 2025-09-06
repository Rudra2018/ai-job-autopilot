from dotenv import load_dotenvnload_dotenv()nimport osn
from extensions.llm_fallback_ollama import fallback_to_ollama
from extensions.llm_vertex import call_vertex_flash_if_available

QUESTIONS = [
    "Tell me about yourself.",
    "How do you handle application security in CI/CD pipelines?",
    "Describe your experience with IAM in AWS.",
    "What’s your approach to logging and monitoring in a cloud environment?"
]

def run_mock_interview(role="Application Security Engineer"):
    transcript = []
    for q in QUESTIONS:
        print(f"🗨️ {q}")
        user_input = input("🧑 Your answer: ")
        try:
            feedback = call_vertex_flash_if_available(f"Give feedback as a senior recruiter:
{interview_transcript}")
Q: {q}
A: {user_input}")
        except:
            feedback = fallback_to_ollama(f"Act as a senior interviewer. Give concise feedback on this answer:
Q: {q}
A: {user_input}")
        print(f"🤖 Feedback: {feedback}\n")
        transcript.append({"question": q, "answer": user_input, "feedback": feedback})
    save_transcript(transcript)
    auto_send_follow_up(transcript)
    return transcript

def save_transcript(transcript):
    import json, os, datetime
    os.makedirs("data/interviews", exist_ok=True)
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H%M")
    with open(f"data/interviews/{date}.json", "w") as f:
        json.dump(transcript, f, indent=2)

def auto_send_follow_up(transcript):
    from worker.gmail_sender import send_email
    from extensions.recruiter_reply_assistant import generate_recruiter_reply
    summary = "Here is a quick summary of my mock interview performance:

"
    summary += "\n".join([f"- {t['question']}\nAnswer: {t['answer']}\nFeedback: {t['feedback']}" for t in transcript])
    message = generate_recruiter_reply(summary, job_title="Security Engineer")
    send_email("recruiter@company.com", "Mock Interview Summary", message)
