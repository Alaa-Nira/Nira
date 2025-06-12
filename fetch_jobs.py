import requests
import json

url = "https://api.reliefweb.int/v1/jobs?appname=nira-jobs&limit=100"
response = requests.get(url)
data = response.json()

jobs = []

for item in data["data"]:
    fields = item["fields"]
    job = {
        "Job Title": fields.get("title", "بدون عنوان"),
        "Company": fields.get("organization", [{}])[0].get("name", "غير معروف"),
        "Location": fields.get("city", "") or fields.get("country", [{}])[0].get("name", "غير معروف"),
        "Tags": [t["name"] for t in fields.get("theme", [])],
        "Description": fields.get("body", "").split("\n")[0] if fields.get("body") else "",
        "Link": fields.get("url", "#"),
        "Deadline": fields.get("deadline", "")[:10] if "deadline" in fields else ""
    }
    jobs.append(job)

# حفظ النتيجة إلى reliefweb_jobs.json
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
