#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Authentication Manager for NIRA Platform
Supports Google OAuth and demo authentication
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app
import requests

class AuthManager:
    def __init__(self, app=None):
        self.app = app
        self.google_client_id = None
        self.google_client_secret = None
        self.demo_mode = True
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة المصادقة مع التطبيق"""
        self.app = app
        
        # محاولة قراءة Google OAuth credentials
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID', 'demo-client-id')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', 'demo-client-secret')
        
        # تحديد ما إذا كنا في وضع التجريب
        self.demo_mode = (
            self.google_client_id == 'demo-client-id' or 
            self.google_client_secret == 'demo-client-secret' or
            not self.google_client_id or 
            not self.google_client_secret
        )
        
        if self.demo_mode:
            app.logger.info("تشغيل نظام المصادقة في الوضع التجريبي")
        else:
            app.logger.info("تشغيل نظام المصادقة مع Google OAuth")
    
    def generate_demo_user(self, email=None):
        """إنشاء مستخدم تجريبي"""
        if not email:
            email = f"demo_user_{secrets.token_hex(4)}@nira.local"
        
        return {
            'id': f"demo_{secrets.token_hex(8)}",
            'email': email,
            'name': 'مستخدم تجريبي',
            'picture': 'https://via.placeholder.com/150',
            'verified_email': True,
            'demo': True,
            'created_at': datetime.now().isoformat()
        }
    
    def login_required(self, f):
        """ديكوريتر للتحقق من تسجيل الدخول"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'يجب تسجيل الدخول للوصول لهذه الميزة',
                    'demo_mode': self.demo_mode
                }), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def is_authenticated(self):
        """التحقق من حالة المصادقة"""
        return 'user' in session and session.get('user') is not None
    
    def get_current_user(self):
        """الحصول على المستخدم الحالي"""
        return session.get('user')
    
    def demo_login(self, email=None):
        """تسجيل دخول تجريبي"""
        if not self.demo_mode:
            return None
        
        user = self.generate_demo_user(email)
        session['user'] = user
        session['authenticated'] = True
        session['login_time'] = datetime.now().isoformat()
        
        return user
    
    def google_login_url(self):
        """إنشاء رابط تسجيل الدخول عبر Google"""
        if self.demo_mode:
            return None
        
        # إنشاء state token للأمان
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': request.url_root + 'api/auth/callback',
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/auth?{query_string}"
    
    def handle_google_callback(self, code, state):
        """معالجة callback من Google OAuth"""
        if self.demo_mode:
            return self.demo_login()
        
        # التحقق من state token
        if state != session.get('oauth_state'):
            raise ValueError("Invalid state token")
        
        # تبديل authorization code بـ access token
        token_data = {
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': request.url_root + 'api/auth/callback'
        }
        
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data
        )
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # الحصول على معلومات المستخدم
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {token_info['access_token']}"}
        )
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # حفظ المستخدم في الجلسة
        user = {
            'id': user_info['id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture', ''),
            'verified_email': user_info.get('verified_email', False),
            'demo': False,
            'created_at': datetime.now().isoformat()
        }
        
        session['user'] = user
        session['authenticated'] = True
        session['login_time'] = datetime.now().isoformat()
        
        return user
    
    def logout(self):
        """تسجيل الخروج"""
        session.pop('user', None)
        session.pop('authenticated', None)
        session.pop('login_time', None)
        session.pop('oauth_state', None)
        
        return True
    
    def get_auth_status(self):
        """الحصول على حالة المصادقة"""
        return {
            'authenticated': self.is_authenticated(),
            'user': self.get_current_user(),
            'demo_mode': self.demo_mode,
            'google_oauth_available': not self.demo_mode
        }

# إنشاء instance عام
auth_manager = AuthManager()

def init_auth(app):
    """تهيئة نظام المصادقة"""
    auth_manager.init_app(app)
    return auth_manager

