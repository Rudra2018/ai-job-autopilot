# 🤖 AI Job Autopilot

A fully automated, AI-powered job search engine that scrapes jobs, matches them to your resume using [JobBERT-v3](https://huggingface.co/TechWolf/JobBERT-v3), generates recruiter messages, applies in real-time using Playwright automation (LinkedIn, Xing, Greenhouse, Lever), and continuously improves via Gemini feedback learning & resume retraining.

---

## ✨ Features

- 🧠 **AI Matching:** Resume ↔ Job description matching with `JobBERT-v3` + Gemini
- 🕵️ **Smart Scraper:** Live scraping from LinkedIn, Xing, Indeed, Glassdoor, Monster, RemoteOK & AngelList/Wellfound (browser & OCR fallback)
- 💌 **Recruiter Messaging:** Auto-generated messages tailored per role/location with tone presets
- 🧪 **A/B Resume Testing:** Batch test resume variants against live job pool
- 🖼️ **OCR Matching:** Parse job screenshots, match to resume (for stealth postings)
- 🔁 **Feedback Learning:** Learns from interview outcomes, retrains resume
- 🔐 **Real Form Automation:** Fills job application forms via Playwright (auto login, CAPTCHA solving)
- 🤖 **LLM Router:** GPT-4o, Gemini 1.5 Pro & Claude 3 Sonnet with automatic fallback
- 🌐 **Cloud Ready:** Deployable via GCP Cloud Build + GitHub Actions CI/CD
- 📊 **Dashboard:** Live application stats & resume performance insights

---

## 🚀 Quickstart

### 1. Clone and Set Up
```bash
git clone https://github.com/Rudra2018/ai-job-autopilot.git
cd ai-job-autopilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 2. Prepare Model
```bash
from sentence_transformers import SentenceTransformer
SentenceTransformer("TechWolf/JobBERT-v3").save("ml_models/jobbert_v3")
```

### 🔧 Environment Setup
```bash
.env.example (copy → .env)
```
# LLM Providers
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key

# Gmail
GMAIL_ADDRESS=you@example.com
GMAIL_APP_PASSWORD=app-specific-password

# LinkedIn/Xing Login
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your-password

# Playwright Setup
PLAYWRIGHT_HEADLESS=true

🤖 Run Autopilot
Full Auto-Apply Flow:
python launch_autopilot.py


What it does:

Loads your resume

Scrapes live jobs from LinkedIn, Xing, Indeed, Glassdoor, Monster, RemoteOK and AngelList

Embeds & matches with JobBERT-v3

Applies to top N matches

Generates recruiter messages

Sends connection requests

Learns from past failures

🧪 Batch Resume Testing

Compare multiple resume variants using:

python tests/batch_resume_runner.py

🖼️ OCR Screenshot Matching

Drop job screenshots into /screenshots:

python extensions/ocr_job_parser.py  # Extracts + Matches

📤 Feedback Loop (Resume Learning)

Every rejection, no callback, or success gets logged. Run:

python extensions/resume_retrain.py


It improves future resume matching and message generation.

🌐 Web Dashboard

Launch React/Vite-based analytics dashboard:

cd ui
npm install
npm run dev

☁️ Cloud Deployment
GCP Cloud Build + GitHub Actions

/cloudbuild/cloudbuild.yaml

.github/workflows/pages.yml

To deploy:

gcloud builds submit --config cloudbuild/cloudbuild.yaml

🔐 Supported Job Platforms
```bash
Platform	Scraping	Form Fill	Notes
LinkedIn	✅	✅	Playwright + CAPTCHA
Xing	✅	✅	Session auto-login
Indeed	✅	❌	Listing scrape
Glassdoor	✅	❌	Listing scrape
Monster	✅	❌	Listing scrape
RemoteOK	✅	❌	Remote roles only
AngelList	✅	❌	Startup jobs (Wellfound)
Greenhouse	✅	✅	Autofill JSON forms
Lever	✅	✅	Multi-step support
```

💡 Customization

extensions/recruiter_playbook.py: Customize recruiter templates

parser/job_title_generator.py: Custom job title + skill logic

ml_models/jobbert_ranker.py: Change vector similarity (cosine/softmax)

📚 Folder Structure
```
ai-job-autopilot/
├── launch_autopilot.py
├── ml_models/            ← JobBERT, Gemini fallback models
├── smart_scraper/        ← Multi-platform job scraping
├── extensions/           ← Resume parser, feedback loop, OCR
├── worker/               ← Auto-connect, email, form fill
├── ui/                   ← React dashboard
├── tests/                ← Resume A/B testing
├── resumes/              ← Store resume variants + logs
├── gcp_pipeline/         ← Cloud build + deploy tools
├── .env.template
├── requirements.txt
└── README.md
```
🤝 Contributing

Feel free to fork, extend, and contribute your own scraping integrations, LLMs, or resume optimizers. PRs welcome.

🧠 Credits

TechWolf/JobBERT-v3

Google Vertex AI / Gemini Pro

HuggingFace Transformers

Playwright Automation

Open Source ✨

📜 License

MIT — free to use, modify, automate, and deploy.

---

Let me know.

