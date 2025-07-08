#!/bin/bash

# سكريپت تشغيل منصة نيرا
# NIRA Platform Startup Script

echo "🚀 بدء تشغيل منصة نيرا..."
echo "🚀 Starting NIRA Platform..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيت Python 3.8 أو أحدث."
    echo "❌ Python 3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

# الانتقال إلى مجلد المشروع
cd "$(dirname "$0")"

# التحقق من وجود البيئة الافتراضية
if [ ! -d "nira_backend/venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    echo "📦 Creating virtual environment..."
    cd nira_backend
    python3 -m venv venv
    cd ..
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
echo "🔧 Activating virtual environment..."
source nira_backend/venv/bin/activate

# تثبيت المتطلبات
echo "📚 تثبيت المتطلبات..."
echo "📚 Installing requirements..."
cd nira_backend
pip install -r requirements.txt
cd ..

# إنشاء مجلدات البيانات
echo "📁 إنشاء مجلدات البيانات..."
echo "📁 Creating data directories..."
mkdir -p data logs

# نسخ ملف البيئة إذا لم يكن موجوداً
if [ ! -f ".env" ]; then
    echo "⚙️ إنشاء ملف البيئة..."
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 يرجى تحديث ملف .env بالإعدادات الصحيحة"
    echo "📝 Please update .env file with correct settings"
fi

# تشغيل مزامنة الوظائف
echo "🔄 مزامنة الوظائف..."
echo "🔄 Syncing jobs..."
python3 advanced_job_scraper.py

# تشغيل الخادم
echo "🌐 تشغيل خادم نيرا..."
echo "🌐 Starting NIRA server..."
cd nira_backend
python src/main.py

echo "✅ تم إيقاف خادم نيرا"
echo "✅ NIRA server stopped"

