import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# ----------------------------- #
# 1) إعداد طلب ReliefWeb (POST) #
# ----------------------------- #

RW_ENDPOINT = "https://api.reliefweb.int/v1/jobs"
PAYLOAD = {
    "appname": "nira",
    "limit": 200,                 # يمكن تكبيره لاحقًا إذا احتجت
    "filter": {
        "conditions": [
            {
                "field": "country",
                "value": "Syrian Arab Republic"
            }
        ]
    },
    # الحقول التي نريد إرجاعها فقط (يزيد السرعة)
    "fields": {
        "include": [
            "title",
            "url",
            "country",
            "city",
            "organization",
            "theme",
            "skill",
            "date",
            "description"
        ]
    }
}

resp = requests.post(
    RW_ENDPOINT,
    params={"appname": "nira"},   # ← يضيف ?appname=nira إلى الـ URL
    json=PAYLOAD,
    timeout=30
)

rw_data = resp.json()["data"]

# ----------------------------- #
# 2) تنظيف وتجهيز البيانات     #
# ----------------------------- #

cleaned_jobs = []

for job in rw_data:
    f = job["fields"]

    # ----------------- العنوان / الرابط -----------------
    title = f.get("title") or "بدون عنوان"
    link  = f.get("url")   or "#"

    # ----------------- المدينة -----------------
    city = f.get("city") or "مدينة غير محددة"

    # ----------------- التواريخ -----------------
    date_posted  = f.get("date", {}).get("posted",  "")[:10]
    date_closing = f.get("date", {}).get("closing", "")[:10]

    # ----------------- الجهة (المنظمة) -----------------
    orgs = f.get("organization", [])
    company = orgs[0]["name"] if orgs else "جهة غير معروفة"

    # ----------------- الوسوم -----------------
    tags = [t["name"] for t in f.get("theme", [])] + \
           [t["name"] for t in f.get("skill", [])]

    # ----------------- الوصف المختصر -----------------
    raw_html = f.get("description", {}).get("content", "")
    soup     = BeautifulSoup(raw_html, "html.parser")
    plain    = soup.get_text(" ", strip=True)

    short_description = (plain[:220] + "…") if len(plain) > 220 else plain
    if not short_description:
        short_description = "لا يوجد وصف متاح"

    # ----------------- بناء القيد النهائي -----------------
    cleaned_jobs.append({
        "Job Title":  title,
        "Company":    company,
        "City":       city,
        "Description": short_description,
        "Tags":        tags,
        "Date":        date_posted,
        "Deadline":    date_closing,
        "Link":        link,
        "Source":      "ReliefWeb"
    })

# ---------------------------------------------- #
# 3) إضافة بصمة وقت (تحفيز الـ commit دائماً)   #
# ---------------------------------------------- #
cleaned_jobs.append({
    "Generated": datetime.now(timezone.utc).isoformat(timespec="seconds")
})

# ----------------------------- #
# 4) حفظ الملف بصيغة UTF-8      #
# ----------------------------- #
with open("reliefweb_jobs.json", "w", encoding="utf-8") as fp:
    json.dump(cleaned_jobs, fp, ensure_ascii=False, indent=2)

print(f"✅ تم حفظ {len(cleaned_jobs)-1} وظيفة من سوريا إلى reliefweb_jobs.json")
