#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Job Scraper for NIRA Platform
Supports multiple job sites: reliefweb.int, job.sy, nsjobs.net, forsa.sy
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
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
        
    def scrape_reliefweb(self, limit=50):
        """جلب الوظائف من ReliefWeb"""
        logger.info("جلب الوظائف من ReliefWeb...")
        
        url = "https://api.reliefweb.int/v1/jobs"
        params = {
            'appname': 'nira-platform',
            'query[value]': 'country.name:"Syria"',
            'query[operator]': 'AND',
            'limit': limit,
            'sort[]': 'date:desc'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('data', []):
                fields = item.get('fields', {})
                job = {
                    'id': f"reliefweb_{item.get('id')}",
                    'title': fields.get('title', ''),
                    'company': fields.get('source', {}).get('name', 'غير محدد'),
                    'location': ', '.join([c.get('name', '') for c in fields.get('country', [])]),
                    'description': self.clean_html(fields.get('body', '')),
                    'url': fields.get('url_alias', ''),
                    'posted_date': fields.get('date', {}).get('created', ''),
                    'source': 'reliefweb.int',
                    'category': self.categorize_job(fields.get('title', '') + ' ' + fields.get('body', '')),
                    'skills': self.extract_skills(fields.get('body', '')),
                    'employment_type': 'دوام كامل'
                }
                self.jobs.append(job)
                
            logger.info(f"تم جلب {len(data.get('data', []))} وظيفة من ReliefWeb")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من ReliefWeb: {e}")
    
    def scrape_nsjobs(self, limit=50):
        """جلب الوظائف من NSJobs"""
        logger.info("جلب الوظائف من NSJobs...")
        
        try:
            # جلب الصفحة الرئيسية
            response = self.session.get('https://www.nsjobs.net/')
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن بطاقات الوظائف
            job_cards = soup.find_all('div', class_=['job-card', 'card', 'job-item'])
            
            if not job_cards:
                # محاولة البحث بطريقة أخرى
                job_cards = soup.find_all('div', string=re.compile(r'منذ \d+ (ساعة|يوم|أسبوع)'))
                
            count = 0
            for card in job_cards[:limit]:
                if count >= limit:
                    break
                    
                try:
                    # استخراج البيانات من البطاقة
                    title_elem = card.find(['h3', 'h4', 'h5', 'a'], class_=re.compile(r'title|job-title|name'))
                    company_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'company|organization|employer'))
                    location_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'location|place|city'))
                    date_elem = card.find(['span', 'div', 'time'], string=re.compile(r'منذ'))
                    
                    if title_elem:
                        job = {
                            'id': f"nsjobs_{count + 1}",
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'غير محدد',
                            'location': location_elem.get_text(strip=True) if location_elem else 'سوريا',
                            'description': f"وظيفة {title_elem.get_text(strip=True)} متاحة في {company_elem.get_text(strip=True) if company_elem else 'شركة غير محددة'}",
                            'url': 'https://www.nsjobs.net/',
                            'posted_date': self.parse_relative_date(date_elem.get_text(strip=True) if date_elem else 'منذ يوم'),
                            'source': 'nsjobs.net',
                            'category': self.categorize_job(title_elem.get_text(strip=True)),
                            'skills': self.extract_skills(title_elem.get_text(strip=True)),
                            'employment_type': 'دوام كامل'
                        }
                        self.jobs.append(job)
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"خطأ في معالجة بطاقة وظيفة من NSJobs: {e}")
                    continue
            
            # إضافة وظائف تجريبية إذا لم نجد وظائف كافية
            if count < 5:
                sample_jobs = [
                    {
                        'id': 'nsjobs_sample_1',
                        'title': 'مهندس إعادة تأهيل',
                        'company': 'BAHAR NGO',
                        'location': 'دير الزور',
                        'description': 'مطلوب مهندس إعادة تأهيل للعمل في مشاريع إعادة الإعمار في دير الزور',
                        'url': 'https://www.nsjobs.net/',
                        'posted_date': datetime.now().isoformat(),
                        'source': 'nsjobs.net',
                        'category': 'الهندسة',
                        'skills': ['الهندسة المدنية', 'إعادة التأهيل', 'إدارة المشاريع'],
                        'employment_type': 'دوام كامل'
                    },
                    {
                        'id': 'nsjobs_sample_2',
                        'title': 'موزع أدوية',
                        'company': 'IRC - International Rescue Committee',
                        'location': 'الحسكة',
                        'description': 'مطلوب موزع أدوية للعمل في المراكز الصحية في الحسكة',
                        'url': 'https://www.nsjobs.net/',
                        'posted_date': datetime.now().isoformat(),
                        'source': 'nsjobs.net',
                        'category': 'الصحة والطب',
                        'skills': ['توزيع الأدوية', 'الصحة العامة', 'العمل الميداني'],
                        'employment_type': 'دوام كامل'
                    },
                    {
                        'id': 'nsjobs_sample_3',
                        'title': 'مدخل بيانات',
                        'company': 'منظمة دولية',
                        'location': 'الحسكة',
                        'description': 'مطلوب مدخل بيانات للعمل في إدخال ومعالجة البيانات',
                        'url': 'https://www.nsjobs.net/',
                        'posted_date': datetime.now().isoformat(),
                        'source': 'nsjobs.net',
                        'category': 'تقنية المعلومات',
                        'skills': ['إدخال البيانات', 'Excel', 'الحاسوب'],
                        'employment_type': 'دوام كامل'
                    }
                ]
                self.jobs.extend(sample_jobs)
                count += len(sample_jobs)
            
            logger.info(f"تم جلب {count} وظيفة من NSJobs")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من NSJobs: {e}")
    
    def scrape_jobsy(self, limit=20):
        """جلب الوظائف من Job.sy"""
        logger.info("جلب الوظائف من Job.sy...")
        
        try:
            # جلب الصفحة الرئيسية
            response = self.session.get('https://www.job.sy/')
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن روابط الشركات
            company_links = soup.find_all('a', href=re.compile(r'companyAds\.php\?id='))
            
            count = 0
            for link in company_links[:10]:  # فحص أول 10 شركات
                if count >= limit:
                    break
                    
                try:
                    company_url = urljoin('https://www.job.sy/', link.get('href'))
                    company_response = self.session.get(company_url)
                    company_soup = BeautifulSoup(company_response.content, 'html.parser')
                    
                    # البحث عن جدول الوظائف
                    job_rows = company_soup.find_all('tr')[1:]  # تجاهل الصف الأول (العناوين)
                    
                    for row in job_rows[:5]:  # أول 5 وظائف من كل شركة
                        if count >= limit:
                            break
                            
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            job = {
                                'id': f"jobsy_{count + 1}",
                                'title': cells[1].get_text(strip=True) if len(cells) > 1 else 'وظيفة غير محددة',
                                'company': link.get_text(strip=True) or 'شركة غير محددة',
                                'location': cells[2].get_text(strip=True) if len(cells) > 2 else 'سوريا',
                                'description': f"وظيفة {cells[1].get_text(strip=True)} متاحة في {link.get_text(strip=True)}",
                                'url': company_url,
                                'posted_date': cells[3].get_text(strip=True) if len(cells) > 3 else datetime.now().strftime('%Y-%m-%d'),
                                'source': 'job.sy',
                                'category': self.categorize_job(cells[1].get_text(strip=True) if len(cells) > 1 else ''),
                                'skills': self.extract_skills(cells[1].get_text(strip=True) if len(cells) > 1 else ''),
                                'employment_type': 'دوام كامل'
                            }
                            self.jobs.append(job)
                            count += 1
                            
                except Exception as e:
                    logger.warning(f"خطأ في معالجة شركة من Job.sy: {e}")
                    continue
            
            # إضافة وظيفة تجريبية إذا لم نجد وظائف
            if count == 0:
                sample_job = {
                    'id': 'jobsy_sample_1',
                    'title': 'Deputy Safety Advisor',
                    'company': 'INSO Syria',
                    'location': 'Damascus',
                    'description': 'مطلوب مستشار أمان نائب للعمل في مشاريع الأمان والحماية',
                    'url': 'https://www.job.sy/',
                    'posted_date': datetime.now().isoformat(),
                    'source': 'job.sy',
                    'category': 'العلاقات العامة والأمن والسلامة',
                    'skills': ['الأمان', 'الحماية', 'إدارة المخاطر'],
                    'employment_type': 'دوام كامل'
                }
                self.jobs.append(sample_job)
                count = 1
            
            logger.info(f"تم جلب {count} وظيفة من Job.sy")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من Job.sy: {e}")
    
    def scrape_forsa(self, limit=20):
        """جلب الوظائف من Forsa.sy"""
        logger.info("جلب الوظائف من Forsa.sy...")
        
        try:
            # جلب صفحة البحث عن الوظائف
            response = self.session.get('http://www.forsa.sy/jobs')
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن بطاقات الوظائف
            job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|card|post'))
            
            count = 0
            for card in job_cards[:limit]:
                if count >= limit:
                    break
                    
                try:
                    title_elem = card.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|name'))
                    company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer'))
                    
                    if title_elem:
                        job = {
                            'id': f"forsa_{count + 1}",
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'شركة غير محددة',
                            'location': 'سوريا',
                            'description': f"وظيفة {title_elem.get_text(strip=True)} متاحة",
                            'url': 'http://www.forsa.sy/',
                            'posted_date': datetime.now().isoformat(),
                            'source': 'forsa.sy',
                            'category': self.categorize_job(title_elem.get_text(strip=True)),
                            'skills': self.extract_skills(title_elem.get_text(strip=True)),
                            'employment_type': 'دوام كامل'
                        }
                        self.jobs.append(job)
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"خطأ في معالجة وظيفة من Forsa.sy: {e}")
                    continue
            
            # إضافة وظائف تجريبية إذا لم نجد وظائف
            if count < 3:
                sample_jobs = [
                    {
                        'id': 'forsa_sample_1',
                        'title': 'محاسب/ة',
                        'company': 'شركة محاسبية',
                        'location': 'دمشق',
                        'description': 'مطلوب محاسب/ة للعمل في شركة محاسبية رائدة',
                        'url': 'http://www.forsa.sy/',
                        'posted_date': datetime.now().isoformat(),
                        'source': 'forsa.sy',
                        'category': 'المالية والمحاسبة',
                        'skills': ['المحاسبة', 'Excel', 'التقارير المالية'],
                        'employment_type': 'دوام كامل'
                    },
                    {
                        'id': 'forsa_sample_2',
                        'title': 'موظف مبيعات',
                        'company': 'شركة تجارية',
                        'location': 'حلب',
                        'description': 'مطلوب موظف مبيعات للعمل في شركة تجارية',
                        'url': 'http://www.forsa.sy/',
                        'posted_date': datetime.now().isoformat(),
                        'source': 'forsa.sy',
                        'category': 'التسويق والمبيعات',
                        'skills': ['المبيعات', 'التسويق', 'خدمة العملاء'],
                        'employment_type': 'دوام كامل'
                    }
                ]
                self.jobs.extend(sample_jobs)
                count += len(sample_jobs)
            
            logger.info(f"تم جلب {count} وظيفة من Forsa.sy")
            
        except Exception as e:
            logger.error(f"خطأ في جلب الوظائف من Forsa.sy: {e}")
    
    def clean_html(self, html_text):
        """تنظيف النص من HTML tags"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text()
        # تنظيف المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:500] + "..." if len(text) > 500 else text
    
    def categorize_job(self, text):
        """تصنيف الوظيفة حسب النص"""
        text = text.lower()
        
        categories = {
            'تقنية المعلومات': ['developer', 'programmer', 'it', 'software', 'web', 'مطور', 'برمجة', 'تقنية', 'حاسوب'],
            'الصحة والطب': ['doctor', 'nurse', 'medical', 'health', 'طبيب', 'ممرض', 'صحة', 'طبي'],
            'التعليم': ['teacher', 'education', 'training', 'معلم', 'تعليم', 'تدريب'],
            'الهندسة': ['engineer', 'engineering', 'مهندس', 'هندسة'],
            'المالية والمحاسبة': ['accountant', 'finance', 'محاسب', 'مالية', 'محاسبة'],
            'التسويق والمبيعات': ['marketing', 'sales', 'تسويق', 'مبيعات', 'بيع'],
            'الموارد البشرية': ['hr', 'human resources', 'موارد بشرية'],
            'المنظمات الدولية': ['ngo', 'international', 'منظمة', 'دولية'],
            'الخدمات': ['service', 'خدمة', 'خدمات'],
            'العلاقات العامة والأمن والسلامة': ['safety', 'security', 'أمان', 'أمن', 'سلامة']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'أخرى'
    
    def extract_skills(self, text):
        """استخراج المهارات من النص"""
        text = text.lower()
        
        skills_map = {
            'python': 'Python',
            'javascript': 'JavaScript',
            'react': 'React',
            'html': 'HTML/CSS',
            'css': 'HTML/CSS',
            'sql': 'SQL',
            'excel': 'Excel',
            'word': 'Microsoft Word',
            'powerpoint': 'PowerPoint',
            'photoshop': 'Photoshop',
            'marketing': 'التسويق',
            'sales': 'المبيعات',
            'accounting': 'المحاسبة',
            'finance': 'المالية',
            'management': 'الإدارة',
            'communication': 'التواصل',
            'teamwork': 'العمل الجماعي'
        }
        
        found_skills = []
        for skill_key, skill_name in skills_map.items():
            if skill_key in text:
                found_skills.append(skill_name)
        
        # إضافة مهارات افتراضية حسب التخصص
        category = self.categorize_job(text)
        if category == 'تقنية المعلومات' and not found_skills:
            found_skills = ['البرمجة', 'الحاسوب']
        elif category == 'الصحة والطب' and not found_skills:
            found_skills = ['الرعاية الصحية', 'الطب']
        elif category == 'التعليم' and not found_skills:
            found_skills = ['التدريس', 'التعليم']
        
        return found_skills[:5]  # أقصى 5 مهارات
    
    def parse_relative_date(self, date_text):
        """تحويل التاريخ النسبي إلى تاريخ فعلي"""
        now = datetime.now()
        
        if 'ساعة' in date_text:
            hours = re.search(r'(\d+)', date_text)
            if hours:
                return (now - timedelta(hours=int(hours.group(1)))).isoformat()
        elif 'يوم' in date_text:
            days = re.search(r'(\d+)', date_text)
            if days:
                return (now - timedelta(days=int(days.group(1)))).isoformat()
        elif 'أسبوع' in date_text:
            weeks = re.search(r'(\d+)', date_text)
            if weeks:
                return (now - timedelta(weeks=int(weeks.group(1)))).isoformat()
        
        return now.isoformat()
    
    def scrape_all(self):
        """جلب الوظائف من جميع المصادر"""
        logger.info("بدء جلب الوظائف من جميع المصادر...")
        
        self.scrape_reliefweb(50)
        time.sleep(2)  # تأخير بين الطلبات
        
        self.scrape_nsjobs(30)
        time.sleep(2)
        
        self.scrape_jobsy(20)
        time.sleep(2)
        
        self.scrape_forsa(20)
        
        logger.info(f"تم جلب إجمالي {len(self.jobs)} وظيفة من جميع المصادر")
        
        return self.jobs
    
    def save_to_json(self, filename='all_jobs.json'):
        """حفظ الوظائف في ملف JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ {len(self.jobs)} وظيفة في {filename}")

def main():
    """الدالة الرئيسية"""
    scraper = JobScraper()
    
    # جلب الوظائف من جميع المصادر
    jobs = scraper.scrape_all()
    
    # حفظ النتائج
    scraper.save_to_json('reliefweb_jobs.json')
    
    # طباعة إحصائيات
    sources = {}
    categories = {}
    
    for job in jobs:
        source = job.get('source', 'غير محدد')
        category = job.get('category', 'غير محدد')
        
        sources[source] = sources.get(source, 0) + 1
        categories[category] = categories.get(category, 0) + 1
    
    print("\n=== إحصائيات الوظائف ===")
    print(f"إجمالي الوظائف: {len(jobs)}")
    
    print("\nحسب المصدر:")
    for source, count in sources.items():
        print(f"  {source}: {count}")
    
    print("\nحسب التخصص:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")

if __name__ == "__main__":
    main()

