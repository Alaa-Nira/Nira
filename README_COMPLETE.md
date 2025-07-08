# منصة نيرا (NIRA) - منصة البحث عن وظائف في سوريا

![NIRA Logo](https://img.shields.io/badge/NIRA-Job%20Platform-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-green?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 📋 نظرة عامة

منصة نيرا هي منصة شاملة للبحث عن الوظائف في سوريا، تجمع الوظائف من مصادر متعددة وتعرضها في واجهة موحدة وسهلة الاستخدام. المنصة تدعم اللغتين العربية والإنجليزية وتوفر ميزات متقدمة للبحث والفلترة.

## ✨ الميزات الرئيسية

### 🔍 البحث والفلترة
- بحث متقدم بالكلمات المفتاحية
- فلترة حسب التخصص (10 تخصصات)
- فلترة حسب المصدر
- ترقيم الصفحات للتصفح السهل

### 🌐 دعم متعدد اللغات
- واجهة باللغتين العربية والإنجليزية
- تبديل سلس بين اللغات
- دعم كامل لاتجاه النص (RTL/LTR)

### 🔐 نظام المصادقة
- تسجيل الدخول عبر Google OAuth
- وضع تجريبي للاختبار
- نظام المفضلة للمستخدمين المسجلين

### 📊 لوحة التحكم الإدارية
- إحصائيات شاملة للنظام
- إدارة الوظائف (إضافة، تعديل، حذف)
- مزامنة الوظائف من المصادر
- سجلات النظام المباشرة

### 🤖 جلب الوظائف التلقائي
- جلب من reliefweb.int
- جلب من job.sy
- جلب من nsjobs.net
- جلب من forsa.sy
- دعم LinkedIn (قيد التطوير)

## 🏗️ البنية التقنية

### Backend
- **Framework**: Flask 2.3
- **Database**: SQLite (قابل للترقية إلى PostgreSQL)
- **ORM**: SQLAlchemy
- **Authentication**: Google OAuth 2.0
- **Web Scraping**: BeautifulSoup4 + Requests

### Frontend
- **HTML5** مع دعم كامل للـ RTL
- **CSS3** مع Flexbox و Grid
- **JavaScript** vanilla للتفاعل
- **Responsive Design** للجوال والحاسوب

### DevOps
- **Docker** للحاويات
- **Docker Compose** للنشر السهل
- **GitHub Actions** للـ CI/CD (قيد الإعداد)

## 🚀 التثبيت والتشغيل

### الطريقة السريعة (باستخدام السكريپت)

```bash
# تحميل المشروع
git clone https://github.com/Alaa-Nira/Nira.git
cd Nira

# تشغيل السكريپت التلقائي
./run.sh
```

### التثبيت اليدوي

#### 1. متطلبات النظام
- Python 3.8 أو أحدث
- pip (مدير حزم Python)
- Git

#### 2. تحميل المشروع
```bash
git clone https://github.com/Alaa-Nira/Nira.git
cd Nira
```

#### 3. إعداد البيئة الافتراضية
```bash
cd nira_backend
python3 -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

#### 4. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

#### 5. إعداد متغيرات البيئة
```bash
cp ../.env.example ../.env
# قم بتحرير ملف .env وإضافة الإعدادات المطلوبة
```

#### 6. مزامنة الوظائف
```bash
cd ..
python3 advanced_job_scraper.py
```

#### 7. تشغيل الخادم
```bash
cd nira_backend
python src/main.py
```

### التشغيل باستخدام Docker

#### 1. بناء الصورة
```bash
docker build -t nira-platform .
```

#### 2. التشغيل باستخدام Docker Compose
```bash
docker-compose up -d
```

## ⚙️ التكوين

### متغيرات البيئة الأساسية

```env
# إعدادات Flask
FLASK_ENV=production
SECRET_KEY=your-very-secret-key-here

# إعدادات Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# إعدادات الخادم
PORT=5000
HOST=0.0.0.0

# وضع التجريبي
DEMO_MODE=true
```

### إعداد Google OAuth

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروع جديد أو اختر مشروع موجود
3. فعّل Google+ API
4. أنشئ OAuth 2.0 credentials
5. أضف الـ Client ID و Client Secret إلى ملف `.env`

## 📖 استخدام المنصة

### للمستخدمين العاديين

#### البحث عن الوظائف
1. اذهب إلى الصفحة الرئيسية
2. استخدم مربع البحث للبحث بالكلمات المفتاحية
3. أو اختر تخصص من القائمة
4. تصفح النتائج واضغط "عرض التفاصيل" للمزيد

#### إدارة المفضلة
1. سجل الدخول عبر Google
2. اضغط على أيقونة القلب في أي وظيفة
3. اذهب إلى صفحة المفضلة لرؤية الوظائف المحفوظة

### للمديرين

#### الوصول إلى لوحة التحكم
```
http://localhost:5000/api/admin
```

#### الميزات المتاحة
- عرض الإحصائيات الشاملة
- مزامنة الوظائف من جميع المصادر
- إدارة الوظائف (حذف، تعديل)
- مراقبة سجلات النظام

## 🔧 تطوير المشروع

### إضافة مصدر وظائف جديد

1. افتح ملف `advanced_job_scraper.py`
2. أضف دالة جديدة للمصدر:

```python
def scrape_new_source():
    """جلب الوظائف من مصدر جديد"""
    jobs = []
    try:
        # كود جلب الوظائف هنا
        pass
    except Exception as e:
        logger.error(f"خطأ في جلب الوظائف من المصدر الجديد: {e}")
    return jobs
```

3. أضف المصدر إلى الدالة الرئيسية `scrape_all_sources()`

### إضافة ميزة جديدة

1. أضف الـ route في ملف `routes/jobs.py`
2. أضف النموذج في `models/user.py` إذا لزم الأمر
3. حدث الواجهة الأمامية في `static/index.html`

## 📊 إحصائيات المشروع

- **53+ وظيفة** متاحة حالياً
- **4 مصادر** للوظائف
- **10 تخصصات** مختلفة
- **دعم كامل** للغتين العربية والإنجليزية
- **لوحة تحكم** إدارية متقدمة

## 🤝 المساهمة

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. أنشئ branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى البranch (`git push origin feature/amazing-feature`)
5. افتح Pull Request

### إرشادات المساهمة

- اكتب كود نظيف ومفهوم
- أضف تعليقات باللغة العربية
- اختبر التغييرات قبل الإرسال
- اتبع نمط الكود الموجود

## 🐛 الإبلاغ عن المشاكل

إذا واجهت أي مشكلة، يرجى:

1. التحقق من [Issues الموجودة](https://github.com/Alaa-Nira/Nira/issues)
2. إنشاء Issue جديد مع:
   - وصف مفصل للمشكلة
   - خطوات إعادة الإنتاج
   - لقطات شاشة إذا أمكن
   - معلومات النظام

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 👥 الفريق

- **علاء** - المطور الرئيسي
- **Manus AI** - مساعد التطوير

## 🙏 شكر وتقدير

- [ReliefWeb](https://reliefweb.int/) لتوفير API الوظائف
- [Flask](https://flask.palletsprojects.com/) للإطار الممتاز
- [Google](https://developers.google.com/) لخدمات OAuth

## 📞 التواصل

- **GitHub**: [Alaa-Nira](https://github.com/Alaa-Nira)
- **Email**: [البريد الإلكتروني]
- **Website**: [الموقع الإلكتروني]

## 🔮 الخطط المستقبلية

- [ ] إضافة دعم LinkedIn API
- [ ] تطبيق جوال (React Native)
- [ ] نظام إشعارات للوظائف الجديدة
- [ ] تحليلات متقدمة للوظائف
- [ ] دعم المزيد من اللغات
- [ ] نظام تقييم الشركات
- [ ] خدمة API عامة للمطورين

---

**منصة نيرا** - نجمع لك أفضل الوظائف في مكان واحد 🚀

*تم التطوير بـ ❤️ في سوريا*

