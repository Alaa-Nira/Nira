import requests
import json

url = "https://api.reliefweb.int/v1/jobs?appname=nira&profile=full&limit=20&filter[field]=country&filter[value]=syria"

response = requests.get(url)
data = response.json()

jobs = []
for job in data["data"]:
    fields = job["fields"]

    title = fields.get("title", "No Title")
    org = fields.get("organization", [{}])[0].get("name", "Unknown")
    location = fields.get("country", [{}])[0].get("name", "Unknown")
    date = fields.get("date", {}).get("posted", "")
    deadline = fields.get("date", {}).get("closing", "")
    description = fields.get("description", {}).get("content", "")[:300]
    link = fields.get("url", "#")

    jobs.append({
        "Job Title": title,
        "Company": org,
        "Location": location,
        "Date": date[:10],
        "Deadline": deadline[:10],
        "Description": description,
        "Link": link
    })

with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
