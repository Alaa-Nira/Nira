import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

# طلب البيانات من ReliefWeb
url = "https://api.reliefweb.int/v1/jobs?appname=nira&limit=100"
response = requests.get(url)
data = response.json()

cleaned_jobs = []

for job in data["data"]:
    fields = job["fields"]

    # تجاهل الوظائف من خارج سوريا
    countries = fields.get("country", [])
    if not any("Syria" in c.get("name", "") for c in countries):
        continue

    # استخراج التفاصيل
    title = fields.get("title", "بدون عنوان")
    url = fields.get("url", "#")
    tags = [t["name"] for t in fields.get("theme", [])] + [t["name"] for t in fields.get("skill", [])]
    city = fields.get("city", "مدينة غير محددة")
    date = fields.get("date", {}).get("posted", "")[:10]
    deadline = fields.get("date", {}).get("closing", "")[:10]

    # الوصف القصير الذكي
    raw_html = fields.get("description", {}).get("content", "")
    soup = BeautifulSoup(raw_html, "html.parser")
    plain_text = soup.get_text(separator=" ", strip=True)
    short_description = plain_text[:220] + ("..." if len(plain_text) > 220 else "")

    # الجهة أو المنظمة
    company = fields.get("organization", [{}])[0].get("name", "جهة غير معروفة")

    cleaned_jobs.append({
        "Job Title": title,
        "Company": company,
        "City": city,
        "Description": short_description or "لا يوجد وصف متاح",
        "Tags": tags,
        "Date": date,
        "Deadline": deadline,
        "Link": url,
        "Source": "ReliefWeb"
    })

# لضمان اختلاف الملف في كل مرة وتحفيز GitHub Actions
if cleaned_jobs:
    cleaned_jobs.append({"Generated": datetime.utcnow().isoformat()})

# حفظ النتائج
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_jobs, f, ensure_ascii=False, indent=2)

print(f"✅ تم حفظ {len(cleaned_jobs)} وظيفة إلى reliefweb_jobs.json")
