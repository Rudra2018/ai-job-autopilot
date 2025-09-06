from dotenv import load_dotenvnload_dotenv()nimport osnimport re

emails = ["hr@company.com", "jobs@startup.io"]
for email in emails:
    print(f"Sending to {email}")
    print("Body: Hi, I’m interested in your open role. Please find my resume attached. ---")

