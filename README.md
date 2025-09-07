# 🤖 AI Job Autopilot

**AI Job Autopilot** is a fully automated, AI-powered job search engine designed to streamline your job hunt. It intelligently scrapes jobs, matches them to your resume using advanced AI models ([JobBERT-v3](https://huggingface.co/TechWolf/JobBERT-v3), Gemini, GPT-4o, Claude 3), generates recruiter messages, and applies for jobs automatically—all while learning and improving from feedback.

---

## ✨ Features

- **AI Matching:** Resume ↔ Job description matching using JobBERT-v3 & Gemini
- **Smart Scraper:** Live scraping from LinkedIn, Xing, Indeed, Glassdoor, Monster, RemoteOK, AngelList/Wellfound (browser & OCR fallback)
- **Recruiter Messaging:** Auto-generated, tailored recruiter messages with customizable tone
- **A/B Resume Testing:** Batch test resume variants against live job pool
- **OCR Matching:** Parse job screenshots and match to your resume for stealth postings
- **Feedback Learning:** Learns from interview outcomes, retrains resume automatically
- **Real Form Automation:** Fills out job application forms via Playwright (auto login, CAPTCHA solving)
- **LLM Router:** Seamless fallback across GPT-4o, Gemini 1.5 Pro, Claude 3 Sonnet
- **Cloud Ready:** Deploy with GCP Cloud Build & GitHub Actions CI/CD
- **Dashboard:** Live application stats & resume performance insights

---

## 🚀 Quickstart

### 1. Clone and Set Up Environment

```bash
git clone https://github.com/Rudra2018/ai-job-autopilot.git
cd ai-job-autopilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Download and Prepare AI Models

```python
from sentence_transformers import SentenceTransformer
SentenceTransformer("TechWolf/JobBERT-v3").save("ml_models/jobbert_v3")
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set the following:

```ini
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
```

---

## 🤖 Running Autopilot

**Full Auto-Apply Flow:**

```bash
python launch_autopilot.py
```

**What happens:**

1. Loads your resume
2. Scrapes live jobs from multiple platforms
3. Matches jobs using JobBERT-v3
4. Applies to top N matches
5. Generates recruiter messages
6. Sends connection requests
7. Learns from outcomes and improves over time

---

## 🧪 Batch Resume Testing

Compare multiple resume variants:

```bash
python tests/batch_resume_runner.py
```

---

## 🖼️ OCR Screenshot Matching

Extract jobs from screenshots (for stealth postings):

1. Place screenshots in `/screenshots`
2. Run:
   ```bash
   python extensions/ocr_job_parser.py
   ```

---

## 📤 Feedback Loop (Resume Learning)

Automatically retrain your resume based on feedback:

```bash
python extensions/resume_retrain.py
```

Each rejection, missed callback, or success is logged and used to improve matching and message generation.

---

## 🌐 Web Dashboard

Launch the React/Vite-based analytics dashboard:

```bash
cd ui
npm install
npm run dev
```

Monitor application stats and resume performance.

---

## ☁️ Cloud Deployment

Supports GCP Cloud Build and GitHub Actions for CI/CD.

- **Cloud Build:** `/cloudbuild/cloudbuild.yaml`
- **GitHub Actions:** `.github/workflows/pages.yml`

Deploy with:

```bash
gcloud builds submit --config cloudbuild/cloudbuild.yaml
```

---

## 🔐 Supported Job Platforms

| Platform   | Scraping | Form Fill | Notes                      |
|------------|:--------:|:---------:|----------------------------|
| LinkedIn   |   ✅     |    ✅     | Playwright + CAPTCHA       |
| Xing       |   ✅     |    ✅     | Session auto-login         |
| Indeed     |   ✅     |    ❌     | Listing scrape             |
| Glassdoor  |   ✅     |    ❌     | Listing scrape             |
| Monster    |   ✅     |    ❌     | Listing scrape             |
| RemoteOK   |   ✅     |    ❌     | Remote roles only          |
| AngelList  |   ✅     |    ❌     | Startup jobs (Wellfound)   |
| Greenhouse |   ✅     |    ✅     | Autofill JSON forms        |
| Lever      |   ✅     |    ✅     | Multi-step support         |

---

## 💡 Customization

- `extensions/recruiter_playbook.py`: Customize recruiter message templates
- `parser/job_title_generator.py`: Custom job title and skill logic
- `ml_models/jobbert_ranker.py`: Change vector similarity (cosine/softmax)

---

## 📚 Folder Structure

```
ai-job-autopilot/
├── launch_autopilot.py
├── ml_models/            # JobBERT, Gemini fallback models
├── smart_scraper/        # Multi-platform job scraping
├── extensions/           # Resume parser, feedback loop, OCR
├── worker/               # Auto-connect, email, form fill
├── ui/                   # React dashboard
├── tests/                # Resume A/B testing
├── resumes/              # Resume variants & logs
├── gcp_pipeline/         # Cloud build & deploy tools
├── .env.template
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

Contributions welcome! Feel free to fork, extend, and add your own scraping integrations, LLMs, or resume optimizers. PRs are encouraged.

---

## 🧠 Credits

- [TechWolf/JobBERT-v3](https://huggingface.co/TechWolf/JobBERT-v3)
- Google Vertex AI / Gemini Pro
- HuggingFace Transformers
- Playwright Automation

---

## 📜 License

MIT — free to use, modify, automate, and deploy.

---

Got questions, ideas, or feedback? Open an issue or reach out!
