import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_reliefweb_jobs_with_full_description(limit=6):
    url = "https://reliefweb.int/updates?search=jobs&appname=jobs&page=1"
    base = "https://reliefweb.int"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    job_links = [
        base + a['href']
        for a in soup.select('.rw-river--title a[href]')
        if '/job/' in a['href']
    ]

    jobs = []

    for link in job_links[:limit]:
        job_resp = requests.get(link, headers=headers)
        job_soup = BeautifulSoup(job_resp.text, 'html.parser')

        title = job_soup.select_one('h1.rw-title')
        title = title.text.strip() if title else "No Title"

        org = job_soup.select_one('.profile--header .profile--name')
        company = org.text.strip() if org else "Unknown"

        deadline = ""
        location = ""
        date = ""
        description = ""

        meta_info = job_soup.select('.content--meta dd')
        meta_labels = job_soup.select('.content--meta dt')

        for label, value in zip(meta_labels, meta_info):
            key = label.text.strip()
            val = value.text.strip()
            if "Closing date" in key:
                deadline = val
            elif "Location" in key:
                location = val
            elif "Published" in key:
                date = val

        content_section = job_soup.select_one('.content--body')
        if content_section:
            full_text = content_section.get_text(separator=' ', strip=True)
            description = full_text[:200] + "..." if len(full_text) > 200 else full_text

        jobs.append({
            "Job Title": title,
            "Company": company,
            "Location": location,
            "Date": date,
            "Deadline": deadline,
            "Description": description,
            "Link": link,
            "Source": "ReliefWeb"
        })

        time.sleep(1.5)

    return jobs

if __name__ == "__main__":
    data = fetch_reliefweb_jobs_with_full_description(limit=6)
    with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ File reliefweb_jobs.json created with latest jobs.")
