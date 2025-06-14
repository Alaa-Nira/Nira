import requests
import json

url = "https://api.reliefweb.int/v1/jobs"
params = {
    "appname": "nira-app",
    "filter[field]": "country",
    "filter[value]": "Syria",
    "sort[]": "date:desc",
    "limit": 100
}

headers = {
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

jobs = []
for item in data["data"]:
    fields = item.get("fields", {})

    job = {
        "Job Title": fields.get("title", "بدون عنوان"),
        "Company": fields.get("organization", [{}])[0].get("name", "غير معروف"),
        "Country": fields.get("country", [{}])[0].get("name", "غير محدد"),
        "City": fields.get("location", {}).get("name", "مدينة غير محددة"),
        "Link": fields.get("url", "#"),
        "Deadline": fields.get("application_deadline", "غير محدد"),
        "Description": fields.get("description", {}).get("text", "")[:150] or "لا يوجد وصف متاح",
        "Tags": [t["name"] for t in fields.get("theme", [])],
        "Date": fields.get("date", {}).get("posted", "")
    }

    if job["Country"] == "Syrian Arab Republic":
        jobs.append(job)

# حفظ الملف
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

print(f"تم حفظ {len(jobs)} وظيفة من سوريا.")
