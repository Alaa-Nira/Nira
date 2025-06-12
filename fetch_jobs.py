import requests
import json

url = "https://api.reliefweb.int/v1/jobs?appname=nira&profile=list&limit=30&filter[field]=country&filter[value]=syria"
response = requests.get(url)
data = response.json()

jobs = []
for job in data["data"]:
    fields = job["fields"]
    jobs.append({
        "Job Title": fields.get("title", "بدون عنوان"),
        "Company": fields.get("organization", [{}])[0].get("name", "غير معروف"),
        "City": fields.get("city", ["غير محددة"])[0],
        "Description": fields.get("description", {}).get("content", "").replace("\n", " ")[:200],
        "Tags": [tag.get("name", "") for tag in fields.get("theme", [])],
        "Category": fields.get("career_categories", [{}])[0].get("name", ""),
        "Type": fields.get("job_type", "غير محدد"),
        "Link": fields.get("url", "#")
    })

with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
