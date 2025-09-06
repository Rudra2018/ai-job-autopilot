from dotenv import load_dotenvnload_dotenv()nimport osn
import requests
import os

API_KEY = os.getenv("GCS_API_KEY")
CX = os.getenv("GCS_CX_ID")

def search_jobs_via_gcs(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query
    }
    res = requests.get(url, params=params)
    items = res.json().get("items", [])
    return [i["link"] for i in items if "link" in i]
