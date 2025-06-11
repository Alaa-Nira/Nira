import requests
import json
from datetime import datetime

# رابط API من موقع ReliefWeb مع فلترة على سوريا
url = "https://api.reliefweb.int/v1/jobs?appname=nira&profile=list&limit=20&filter[field]=country&filter[value]=syria"

# طلب البيانات من API
response = requests.get(url)
data = response.json()

# استخراج الوظائف من البيانات
jobs = []
for job in data["data"]:
    fields = job["fields"]
    title = fields["title"]
    org = fields.get("organization", [{}])[0].get("name", "Unknown")
    country = fields.get("country", [{}])[0].get("name", "Unknown")
    date = fields["date"]["posted"][:10]  # YYYY-MM-DD
    link = fields["url"]

    jobs.append({
        "Job Title": title,
        "Company": org,
        "Location": country,
        "Date": date,
        "Link": link
    })

# حفظ الوظائف في ملف reliefweb_jobs.json
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

print("✅ Jobs data fetched and saved to reliefweb_jobs.json")
