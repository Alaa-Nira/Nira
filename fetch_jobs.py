import requests, json, sys
from datetime import datetime
from bs4 import BeautifulSoup

API = "https://api.reliefweb.int/v1/jobs"
PARAMS = {
    "appname": "nira",
    "limit": 100,
    # الفلترة داخل الـ API بدلاً من التصفية اليدوية
    "filter[field]": "country.name",
    "filter[value]": "Syria"
}

try:
    resp = requests.get(API, params=PARAMS, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
except Exception as e:
    # اطبع محتوى الاستجابة ليسهل عليك التشخيص
    print("🔴 API error:", e)
    print("Response text:", resp.text[:800])
    sys.exit(1)

if "data" not in payload:
    print("🔴 المفتاح data غير موجود – محتوى الرد:")
    print(json.dumps(payload, ensure_ascii=False, indent=2)[:800])
    sys.exit(1)

cleaned_jobs = []
for job in payload["data"]:
    f = job["fields"]
    cleaned_jobs.append({
        "Job Title": f.get("title", "بدون عنوان"),
        "Company"  : (f.get("organization") or [{}])[0].get("name", "جهة غير معروفة"),
        "City"     : f.get("city", "مدينة غير محددة"),
        "Description": BeautifulSoup(
            f.get("description", {}).get("content", ""), "html.parser"
        ).get_text(" ", strip=True)[:220] + "…",
        "Tags"     : [t["name"] for t in f.get("theme", [])] +
                     [t["name"] for t in f.get("skill", [])],
        "Date"     : f.get("date", {}).get("posted", "")[:10],
        "Deadline" : f.get("date", {}).get("closing", "")[:10],
        "Link"     : f.get("url", "#"),
        "Source"   : "ReliefWeb"
    })

# لإجبار GitHub على اكتشاف تغيّر الملف
cleaned_jobs.append({"Generated": datetime.utcnow().isoformat()})

with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_jobs, f, ensure_ascii=False, indent=2)

print(f"✅ تم حفظ {len(cleaned_jobs)-1} وظيفة.")
