import requests
import json
from bs4 import BeautifulSoup
import re

def extract_city(location_str):
    if not location_str:
        return "مدينة غير محددة"
    if "," in location_str:
        return location_str.split(",")[0].strip()
    return location_str.strip()

def extract_short_description(html_text):
    if not html_text:
        return "لا يوجد وصف متاح."
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text().strip()
    # خذ أول 200 حرف أو أول جملة مفيدة
    match = re.search(r'(.{30,200}[.؟!])', text)
    return match.group(1).strip() if match else text[:200]

url = "https://api.reliefweb.int/v1/jobs?appname=apidoc&profile=full&limit=100"
response = requests.get(url)
data = response.json()

jobs = []
for job in data["data"]:
    fields = job["fields"]
    if "Syria" not in fields["country"][0]["name"]:
        continue  # تخطى الوظائف غير السورية

    title = fields.get("title", "")
    organization = fields["organization"][0]["name"] if fields.get("organization") else "جهة غير معروفة"
    location_raw = fields["location"][0]["name"] if fields.get("location") else ""
    city = extract_city(location_raw)
    description_raw = fields.get("body", "")
    description = extract_short_description(description_raw)
    tags = [theme["name"] for theme in fields.get("theme", [])] + \
           [jobtype["name"] for jobtype in fields.get("job_type", [])]
    date = fields.get("date", {}).get("posted", "")[:10]
    deadline = fields.get("date", {}).get("closing", "")[:10]
    link = fields.get("url", "")

    jobs.append({
        "Job Title": title,
        "Company": organization,
        "City": city,
        "Description": description,
        "Tags": tags,
        "Date": date,
        "Deadline": deadline,
        "Link": link,
        "Source": "ReliefWeb"
    })

# فقط آخر 6 وظائف
with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs[:6], f, ensure_ascii=False, indent=2)
