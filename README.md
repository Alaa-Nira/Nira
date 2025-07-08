# منصة نيرا (NIRA) - منصة البحث عن الوظائف في سوريا

## نظرة عامة

نيرا هي منصة متطورة لجمع الوظائف من مختلف المصادر في سوريا وعرضها في مكان واحد. تهدف المنصة إلى تسهيل عملية البحث عن الوظائف للباحثين عن العمل وتوفير الوقت والجهد.

## الميزات الرئيسية

### ✅ الميزات المكتملة

- **جمع الوظائف من مصادر متعددة**: reliefweb.int, job.sy, nsjobs.net, forsa.sy
- **واجهة مستخدم متقدمة**: تصميم حديث ومتجاوب مع جميع الأجهزة
- **دعم اللغتين**: العربية والإنجليزية مع تبديل سلس
- **نظام بحث متقدم**: بحث بالكلمات المفتاحية والتخصصات
- **فلترة ذكية**: حسب التخصص والمصدر والموقع
- **إحصائيات مباشرة**: عدد الوظائف والشركات والمصادر
- **تصنيف حسب التخصص**: 10 تخصصات رئيسية
- **API متكامل**: RESTful API للوصول للبيانات
- **قاعدة بيانات محسنة**: SQLite مع نماذج محسنة

### 🔄 الميزات قيد التطوير

- **تسجيل الدخول عبر Google**: يحتاج إعداد OAuth credentials
- **نظام المفضلة**: مكتمل في الكود، يحتاج تسجيل دخول
- **لوحة التحكم الإدارية**: للإدارة والإحصائيات
- **web scrapers إضافية**: لمواقع job.sy و nsjobs.net و forsa.sy

## التقنيات المستخدمة

### Backend
- **Flask**: إطار عمل Python للخادم
- **SQLAlchemy**: ORM لقاعدة البيانات
- **SQLite**: قاعدة البيانات
- **Flask-CORS**: دعم CORS
- **Requests & BeautifulSoup**: لجلب البيانات من المواقع

### Frontend
- **HTML5 & CSS3**: هيكل وتصميم الصفحات
- **JavaScript (Vanilla)**: التفاعل والديناميكية
- **Tailwind CSS**: إطار عمل CSS
- **Font Awesome**: الأيقونات
- **Google Fonts**: الخطوط (Tajawal للعربية، Poppins للإنجليزية)

## هيكل المشروع

```
nira-project/
├── nira_backend/                 # Flask Backend
│   ├── src/
│   │   ├── main.py              # نقطة دخول التطبيق
│   │   ├── models/              # نماذج قاعدة البيانات
│   │   │   └── user.py          # نماذج المستخدم والوظائف والمفضلة
│   │   ├── routes/              # مسارات API
│   │   │   ├── auth.py          # مصادقة Google OAuth
│   │   │   └── jobs.py          # API الوظائف والمفضلة
│   │   └── static/              # الملفات الثابتة
│   │       └── index.html       # الواجهة الأمامية
│   ├── requirements.txt         # متطلبات Python
│   └── venv/                    # البيئة الافتراضية
├── enhanced_job_scraper.py      # سكريبت جلب الوظائف المحسن
├── reliefweb_jobs.json         # بيانات الوظائف
└── README.md                   # هذا الملف
```

## التثبيت والتشغيل

### 1. تثبيت المتطلبات

```bash
cd nira_backend
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. تشغيل الخادم

```bash
python src/main.py
```

الموقع سيكون متاحاً على: `http://localhost:5000`

### 3. جلب الوظائف

```bash
# جلب وظائف جديدة
python enhanced_job_scraper.py

# مزامنة مع قاعدة البيانات
curl -X POST http://localhost:5000/api/sync
```

## API Documentation

### الوظائف

- `GET /api/jobs` - جلب قائمة الوظائف
  - Parameters: `page`, `per_page`, `search`, `category`, `source`
- `GET /api/jobs/{id}` - جلب وظيفة محددة
- `POST /api/sync` - مزامنة الوظائف من ملف JSON

### الإحصائيات

- `GET /api/stats` - جلب إحصائيات المنصة
- `GET /api/categories` - جلب قائمة التخصصات

### المصادقة (يحتاج إعداد)

- `GET /api/auth/login` - تسجيل الدخول عبر Google
- `POST /api/auth/logout` - تسجيل الخروج
- `GET /api/auth/check` - فحص حالة المصادقة

### المفضلة (يحتاج تسجيل دخول)

- `GET /api/favorites` - جلب الوظائف المفضلة
- `POST /api/favorites` - إضافة وظيفة للمفضلة
- `DELETE /api/favorites/{job_id}` - إزالة من المفضلة

## الإعدادات المطلوبة

### Google OAuth (اختياري)

لتفعيل تسجيل الدخول عبر Google، يجب إعداد:

1. إنشاء مشروع في Google Cloud Console
2. تفعيل Google+ API
3. إنشاء OAuth 2.0 credentials
4. تحديث المتغيرات في `main.py`:

```python
GOOGLE_CLIENT_ID = "your-actual-client-id"
GOOGLE_CLIENT_SECRET = "your-actual-client-secret"
```

## المصادر المدعومة

1. **ReliefWeb** (مكتمل): https://reliefweb.int/jobs
2. **Job.sy** (قيد التطوير): https://www.job.sy/
3. **NSJobs** (قيد التطوير): https://www.nsjobs.net/
4. **Forsa.sy** (قيد التطوير): http://www.forsa.sy/
5. **LinkedIn** (مخطط): للمستقبل

## التخصصات المدعومة

- تقنية المعلومات
- الصحة والطب
- التعليم
- الهندسة
- المالية والمحاسبة
- التسويق والمبيعات
- الموارد البشرية
- المنظمات الدولية
- الخدمات
- أخرى

## الحالة الحالية

### ✅ مكتمل
- Backend API كامل
- Frontend متجاوب
- نظام البحث والفلترة
- دعم اللغتين
- جلب الوظائف من ReliefWeb
- قاعدة البيانات والنماذج

### 🔄 قيد العمل
- Google OAuth setup
- Web scrapers للمواقع الإضافية
- لوحة التحكم الإدارية
- تحسينات الأداء

### 📋 مخطط
- تطبيق موبايل
- إشعارات الوظائف الجديدة
- نظام التقييمات
- تكامل مع LinkedIn

## المساهمة

المشروع مفتوح للمساهمات. يرجى:

1. Fork المشروع
2. إنشاء branch جديد للميزة
3. Commit التغييرات
4. Push إلى Branch
5. إنشاء Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT.

## التواصل

للاستفسارات والدعم، يرجى التواصل عبر GitHub Issues.

---

**نيرا - ابحث عن وظيفتك المثالية في سوريا** 🇸🇾

