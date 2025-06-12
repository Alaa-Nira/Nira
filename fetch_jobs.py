import requests
import json

url = "https://api.reliefweb.int/v1/jobs"
params = {
    "appname": "nira-job-fetcher",
    "filter[field]": "country",
    "filter[value]": "Syria",
    "limit": 50,
    "profile": "full"
}

response = requests.get(url, params=params)
data = response.json()

jobs = []

for item in data["data"]:
    fields = item["fields"]
    
    city = ""
    if fields.get("location"):
        loc = fields["location"][0]
        city = loc.get("name", "").split(",")[0].strip()

    jobs.append({
        "Job Title": fields.get("title", ""),
        "Company": fields.get("organization", {}).get("name", ""),
        "City": city,
        "Country": fields.get("country", [{}])[0].get("name", ""),
        "Deadline": fields.get("date", {}).get("closing", ""),
        "Link": fields.get("url", ""),
        "Description": fields.get("description", {}).get("text", "")[:200]
    })

with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

print("تم إنشاء الملف reliefweb_jobs.json بنجاح.")
