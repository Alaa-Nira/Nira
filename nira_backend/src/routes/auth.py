from flask import Blueprint, request, jsonify, session, redirect
from auth_manager import auth_manager
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """بدء عملية تسجيل الدخول"""
    try:
        # إعادة توجيه إلى Google OAuth
        google_url = auth_manager.google_login_url()
        if google_url:
            return redirect(google_url)
        else:
            return jsonify({
                'error': 'OAuth configuration error',
                'message': 'خطأ في إعدادات Google OAuth'
            }), 500
                
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {e}")
        return jsonify({
            'error': 'Login failed',
            'message': 'فشل في تسجيل الدخول'
        }), 500

@auth_bp.route('/callback', methods=['GET'])
def callback():
    """معالجة callback من Google OAuth"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({
                'error': 'OAuth error',
                'message': f'خطأ في المصادقة: {error}'
            }), 400
        
        if not code:
            return jsonify({
                'error': 'Missing authorization code',
                'message': 'رمز التفويض مفقود'
            }), 400
        
        # معالجة callback
        user = auth_manager.handle_google_callback(code, state)
        
        if user:
            return redirect('/?login=success')
        else:
            return redirect('/?login=error')
            
    except Exception as e:
        logger.error(f"خطأ في callback: {e}")
        return redirect('/?login=error')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """تسجيل الخروج"""
    try:
        auth_manager.logout()
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الخروج بنجاح'
        })
    except Exception as e:
        logger.error(f"خطأ في تسجيل الخروج: {e}")
        return jsonify({
            'error': 'Logout failed',
            'message': 'فشل في تسجيل الخروج'
        }), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """فحص حالة المصادقة"""
    try:
        status = auth_manager.get_auth_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"خطأ في فحص المصادقة: {e}")
        return jsonify({
            'authenticated': False,
            'user': None,
            'demo_mode': auth_manager.demo_mode,
            'error': 'فشل في فحص حالة المصادقة'
        })

@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """تسجيل دخول تجريبي (للاختبار)"""
    try:
        if not auth_manager.demo_mode:
            return jsonify({
                'error': 'Demo mode not available',
                'message': 'الوضع التجريبي غير متاح'
            }), 403
        
        data = request.get_json() or {}
        email = data.get('email', 'demo@nira.local')
        
        user = auth_manager.demo_login(email)
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول التجريبي بنجاح',
            'user': user,
            'demo_mode': True
        })
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول التجريبي: {e}")
        return jsonify({
            'error': 'Demo login failed',
            'message': 'فشل في تسجيل الدخول التجريبي'
        }), 500

