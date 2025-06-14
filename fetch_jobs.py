import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_jobs(limit=6):
    base_url = "https://reliefweb.int"
    search_url = f"{base_url}/jobs?search=syrian&appname=jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    jobs = []

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        job_links = [a['href'] for a in soup.select(".rw-river--title a[href]") if '/job/' in a['href']]
        job_links = list(dict.fromkeys(job_links))  # remove duplicates
    except Exception as e:
        print("❌ Failed to fetch links:", e)
        return []

    for link in job_links[:limit]:
        try:
            job_url = base_url + link
            res = requests.get(job_url, headers=headers)
            detail = BeautifulSoup(res.text, "html.parser")

            title = detail.select_one("h1.rw-title")
            title = title.text.strip() if title else "بدون عنوان"

            company = detail.select_one(".profile--name")
            company = company.text.strip() if company else "جهة غير معروفة"

            date = ""
            deadline = ""
            city = "مدينة غير محددة"

            for dt, dd in zip(detail.select(".content--meta dt"), detail.select(".content--meta dd")):
                key = dt.text.strip()
                value = dd.text.strip()
                if "Closing" in key:
                    deadline = value
                elif "Location" in key:
                    city = value
                elif "Published" in key:
                    date = value

            description_div = detail.select_one(".content--body")
            description = description_div.get_text(separator=' ', strip=True) if description_div else ""
            short_description = description[:220] + "..." if len(description) > 220 else description

            jobs.append({
                "Job Title": title,
                "Company": company,
                "City": city,
                "Date": date,
                "Deadline": deadline,
                "Description": short_description,
                "Link": job_url,
                "Source": "ReliefWeb"
            })

            time.sleep(2)

        except Exception as e:
            print(f"⚠️ Skipping {link} due to error:", e)
            continue

    return jobs


if __name__ == "__main__":
    data = fetch_jobs(limit=6)
    with open("reliefweb_jobs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data)} jobs to reliefweb_jobs.json")
