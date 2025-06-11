import requests
import json
from datetime import datetime

# طلب الوظائف من سوريا عبر ReliefWeb
url = "https://api.reliefweb.int/v1/jobs?appname=nira&profile=list&limit=20&filter[field]=country&filter[value]=syria"

response = requests.get(url)
data = response.json()

# استخراج الوظائف وتبسيطها إلى صيغة بسيطة
jobs = []
for job in data["data"]:
    title = job["fields"]["title"]
    org = job["fields"].get("organization", [{}])[0].get("name", "Unknown")
    country = job["fields"].get("country", [{}])[0].get("name", "Unknown")
    date = job.get("fields", {}).get("date", {}).get("posted", "")[:10]
    link = job["fields"]["url"]

    jobs.append({
        "Job Title": title,
        "Company": org,
        "Location": country,
        "Date": date,
        "Link": link
    })

# حفظها في ملف reliefweb_jobs.json
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
