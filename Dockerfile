# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY nira_backend/requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY nira_backend/src ./src
COPY reliefweb_jobs.json .
COPY advanced_job_scraper.py .

# إنشاء مجلد قاعدة البيانات
RUN mkdir -p /app/data

# تعيين المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["python", "src/main.py"]

