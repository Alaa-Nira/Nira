import os
import sys
# DON'T CHANGE: Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models.user import db
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from auth_manager import init_auth
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nira-secret-key-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nira.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تفعيل CORS
    CORS(app, supports_credentials=True, origins=['*'])
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تهيئة نظام المصادقة المحسن
    init_auth(app)
    
    # تسجيل blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    
    # إنشاء الجداول
    with app.app_context():
        db.create_all()
        logger.info("تم إنشاء جداول قاعدة البيانات")
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    # خدمة الملفات الثابتة
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    # API health check
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'message': 'NIRA API is running',
            'version': '2.0.0'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # تشغيل الخادم
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info("تشغيل خادم NIRA على المنفذ 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)

