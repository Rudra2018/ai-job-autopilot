from dotenv import load_dotenv
load_dotenv()
import os
import re

emails = ["hr@company.com", "jobs@startup.io"]
for email in emails:
    print(f"Sending to {email}")
    print("Body: Hi, I’m interested in your open role. Please find my resume attached. ---")

