import requests
import json
from bs4 import BeautifulSoup

URL = "https://api.reliefweb.int/v1/jobs"
PARAMS = {
    "appname": "nira-jobs",
    "limit": 100,
    "profile": "full"
}

response = requests.get(URL, params=PARAMS)
data = response.json()

jobs = []

for item in data["data"]:
    fields = item["fields"]

    # فلترة الوظائف في سوريا فقط
    country_list = fields.get("country", [])
    if not any(country.get("name", "") == "Syria" for country in country_list):
        continue

    title = fields.get("title", "بدون عنوان")
    org = fields.get("organization", [{}])[0].get("name", "جهة غير معروفة")
    body_html = fields.get("body", "")
    link = fields.get("url", "#")
    tags = [t.get("name") for t in fields.get("theme", [])]
    deadline = fields.get("closing_date", "")[:10]
    source = "ReliefWeb"

    # استخراج المدينة من النص الكامل (body)
    soup = BeautifulSoup(body_html, "html.parser")
    text = soup.get_text().strip().replace("\n", " ")

    # استخراج وصف قصير
    desc = "لا يوجد وصف متاح"
    for paragraph in soup.find_all("p"):
        content = paragraph.get_text(strip=True)
        if 50 < len(content) < 300:
            desc = content
            break

    # استخراج المدينة إذا ذُكرت
    location = fields.get("location", [])
    city = location[0].get("name", "مدينة غير محددة") if location else "مدينة غير محددة"

    jobs.append({
        "Job Title": title,
        "Company": org,
        "City": city,
        "Description": desc,
        "Tags": tags,
        "Deadline": deadline,
        "Link": link,
        "Source": source
    })

with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
