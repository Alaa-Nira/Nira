#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Job Scraper for NIRA Platform
Fetches jobs from multiple sources: reliefweb, job.sy, nsjobs.net, forsa.sy
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.jobs = []

    def fetch_reliefweb_jobs(self):
        """جلب الوظائف من reliefweb.int"""
        try:
            logger.info("جلب الوظائف من reliefweb.int...")
            url = "https://api.reliefweb.int/v1/jobs?appname=nira&profile=full&limit=50&filter[field]=country&filter[value]=syria"
            response = self.session.get(url)
            data = response.json()

            for job in data.get("data", []):
                fields = job.get("fields", {})
                
                job_data = {
                    "title": fields.get("title", "No Title"),
                    "company": fields.get("organization", [{}])[0].get("name", "Unknown"),
                    "location": fields.get("country", [{}])[0].get("name", "Syria"),
                    "date_posted": fields.get("date", {}).get("posted", "")[:10],
                    "deadline": fields.get("date", {}).get("closing", "")[:10],
                    "description": fields.get("description", {}).get("content", "")[:300],
                    "link": fields.get("url", "#"),
                    "source": "reliefweb.int",
                    "job_type": "دوام كامل",
                    "category": "منظمات دولية"
                }
                self.jobs.append(job_data)
            
            logger.info(f"تم جلب {len([j for j in self.jobs if j['source'] == 'reliefweb.int'])} وظيفة من reliefweb")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من reliefweb: {e}")

    def fetch_nsjobs_jobs(self):
        """جلب الوظائف من nsjobs.net"""
        try:
            logger.info("جلب الوظائف من nsjobs.net...")
            # هذا مثال أساسي - يحتاج تطوير أكثر حسب هيكل الموقع الفعلي
            url = "https://www.nsjobs.net/"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن الوظائف في الصفحة الرئيسية
            # هذا يحتاج تحليل أعمق لهيكل HTML الفعلي
            job_cards = soup.find_all('div', class_='job-card') or soup.find_all('div', class_='recent-job')
            
            for card in job_cards[:20]:  # أخذ أول 20 وظيفة
                try:
                    title = card.find('h3') or card.find('h4') or card.find('a')
                    company = card.find('span', class_='company') or card.find('div', class_='company')
                    location = card.find('span', class_='location') or card.find('div', class_='location')
                    
                    if title:
                        job_data = {
                            "title": title.get_text(strip=True),
                            "company": company.get_text(strip=True) if company else "غير معلن",
                            "location": location.get_text(strip=True) if location else "شمال سوريا",
                            "date_posted": datetime.now().strftime("%Y-%m-%d"),
                            "deadline": "",
                            "description": "وظيفة متاحة في شمال سوريا",
                            "link": "https://www.nsjobs.net/",
                            "source": "nsjobs.net",
                            "job_type": "دوام كامل",
                            "category": "متنوع"
                        }
                        self.jobs.append(job_data)
                except Exception as e:
                    continue
            
            logger.info(f"تم جلب {len([j for j in self.jobs if j['source'] == 'nsjobs.net'])} وظيفة من nsjobs.net")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من nsjobs.net: {e}")

    def fetch_forsa_jobs(self):
        """جلب الوظائف من forsa.sy"""
        try:
            logger.info("جلب الوظائف من forsa.sy...")
            url = "http://www.forsa.sy/jobs.html"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن بطاقات الوظائف
            job_cards = soup.find_all('div', class_='job-card') or soup.find_all('div', class_='card')
            
            for card in job_cards[:15]:  # أخذ أول 15 وظيفة
                try:
                    title = card.find('h3') or card.find('h4') or card.find('h5')
                    company = card.find('span', class_='company') or card.find('div', class_='company')
                    
                    if title:
                        job_data = {
                            "title": title.get_text(strip=True),
                            "company": company.get_text(strip=True) if company else "غير معلن",
                            "location": "سوريا",
                            "date_posted": datetime.now().strftime("%Y-%m-%d"),
                            "deadline": "",
                            "description": "فرصة عمل متاحة في سوريا",
                            "link": "http://www.forsa.sy/",
                            "source": "forsa.sy",
                            "job_type": "دوام كامل",
                            "category": "متنوع"
                        }
                        self.jobs.append(job_data)
                except Exception as e:
                    continue
            
            logger.info(f"تم جلب {len([j for j in self.jobs if j['source'] == 'forsa.sy'])} وظيفة من forsa.sy")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من forsa.sy: {e}")

    def add_sample_jobs(self):
        """إضافة وظائف تجريبية للاختبار"""
        sample_jobs = [
            {
                "title": "مطور ويب",
                "company": "شركة التقنية الحديثة",
                "location": "دمشق",
                "date_posted": datetime.now().strftime("%Y-%m-%d"),
                "deadline": "2025-08-15",
                "description": "مطلوب مطور ويب لديه خبرة في تقنيات Front-end مع معرفة جيدة بالـ React.js",
                "link": "#",
                "source": "nira.local",
                "job_type": "دوام كامل",
                "category": "IT",
                "skills": ["HTML/CSS", "JavaScript", "React"]
            },
            {
                "title": "ممرضة مسجلة",
                "company": "المشفى الوطني",
                "location": "حلب",
                "date_posted": datetime.now().strftime("%Y-%m-%d"),
                "deadline": "2025-07-25",
                "description": "مطلوب ممرضات ذوات خبرة للعمل في قسم الطوارئ بالمشفى الوطني",
                "link": "#",
                "source": "nira.local",
                "job_type": "دوام جزئي",
                "category": "رعاية صحية",
                "skills": ["تمريض", "طوارئ", "رعاية صحية"]
            },
            {
                "title": "مدير مشروع",
                "company": "منظمة إنسانية دولية",
                "location": "شمال سوريا",
                "date_posted": datetime.now().strftime("%Y-%m-%d"),
                "deadline": "2025-12-31",
                "description": "مطلوب مدير مشروع بخبرة لا تقل عن 5 سنوات في إدارة المشاريع الإنسانية",
                "link": "#",
                "source": "nira.local",
                "job_type": "دوام كامل",
                "category": "إدارة المشاريع",
                "skills": ["إدارة المشاريع", "التخطيط", "القيادة"]
            }
        ]
        
        self.jobs.extend(sample_jobs)
        logger.info(f"تم إضافة {len(sample_jobs)} وظيفة تجريبية")

    def clean_and_format_jobs(self):
        """تنظيف وتنسيق البيانات"""
        cleaned_jobs = []
        for job in self.jobs:
            # تنظيف النصوص
            job['title'] = re.sub(r'<[^>]+>', '', str(job.get('title', ''))).strip()
            job['company'] = re.sub(r'<[^>]+>', '', str(job.get('company', ''))).strip()
            job['description'] = re.sub(r'<[^>]+>', '', str(job.get('description', ''))).strip()
            
            # التأكد من وجود البيانات الأساسية
            if job['title'] and job['title'] != 'No Title':
                # تحويل إلى التنسيق المطلوب للواجهة الأمامية
                formatted_job = {
                    "Job Title": job['title'],
                    "Company": job['company'] or "غير مذكورة",
                    "Location": job['location'] or "غير مذكور",
                    "Date": job['date_posted'] or datetime.now().strftime("%Y-%m-%d"),
                    "Deadline": job['deadline'] or "غير مذكور",
                    "Description": job['description'] or "لا يوجد وصف متاح",
                    "Link": job['link'] or "#",
                    "Source": job['source'],
                    "Job Type": job.get('job_type', 'دوام كامل'),
                    "Category": job.get('category', 'متنوع'),
                    "Skills": job.get('skills', [])
                }
                cleaned_jobs.append(formatted_job)
        
        return cleaned_jobs

    def save_jobs(self, filename="reliefweb_jobs.json"):
        """حفظ الوظائف في ملف JSON"""
        try:
            cleaned_jobs = self.clean_and_format_jobs()
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cleaned_jobs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حفظ {len(cleaned_jobs)} وظيفة في {filename}")
            return len(cleaned_jobs)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الوظائف: {e}")
            return 0

    def run(self):
        """تشغيل جميع عمليات جلب الوظائف"""
        logger.info("بدء عملية جلب الوظائف من جميع المصادر...")
        
        # جلب من جميع المصادر
        self.fetch_reliefweb_jobs()
        time.sleep(2)  # تأخير بسيط بين الطلبات
        
        self.fetch_nsjobs_jobs()
        time.sleep(2)
        
        self.fetch_forsa_jobs()
        time.sleep(2)
        
        # إضافة وظائف تجريبية
        self.add_sample_jobs()
        
        # حفظ النتائج
        total_jobs = self.save_jobs()
        
        logger.info(f"انتهت عملية جلب الوظائف. إجمالي الوظائف: {total_jobs}")
        return total_jobs

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()

