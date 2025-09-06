from dotenv import load_dotenv
load_dotenv()
import os
import yaml

with open("config/user_profile.yaml", "r") as f:
    user_config = yaml.safe_load(f)

job_targets = user_config.get("job_targets", [])
def send_connection_requests():
    for job in job_targets:
        message = f"Hi, I'm interested in {job.get('title')} roles in {job.get('location')}. Let's connect!"
        print(f"🤝 Sending LinkedIn/Xing connection request with message: {message}")
