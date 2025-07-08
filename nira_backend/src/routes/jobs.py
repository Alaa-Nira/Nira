from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
from models.user import db, User, Job, Favorite, Category
from auth_manager import auth_manager
import json
import os
from datetime import datetime
import logging
import os

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """الحصول على قائمة الوظائف مع إمكانية البحث والفلترة"""
    try:
        # معاملات البحث
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        location = request.args.get('location', '')
        source = request.args.get('source', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        # بناء الاستعلام
        query = Job.query
        
        if search:
            query = query.filter(
                or_(
                    Job.title.contains(search),
                    Job.company.contains(search),
                    Job.description.contains(search)
                )
            )
        
        if category:
            query = query.filter(Job.category.contains(category))
        
        if location:
            query = query.filter(Job.location.contains(location))
        
        if source:
            query = query.filter(Job.source == source)
        
        # ترتيب حسب التاريخ
        query = query.order_by(Job.created_at.desc())
        
        # تطبيق التصفح
        jobs = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # تحويل إلى قاموس
        jobs_data = []
        user_favorites = []
        
        # إذا كان المستخدم مسجل دخول، جلب مفضلاته
        if 'user_id' in session:
            user_favorites = [f.job_id for f in Favorite.query.filter_by(user_id=session['user_id']).all()]
        
        for job in jobs.items:
            job_dict = job.to_dict()
            job_dict['is_favorite'] = job.id in user_favorites
            jobs_data.append(job_dict)
        
        return jsonify({
            'jobs': jobs_data,
            'pagination': {
                'page': jobs.page,
                'pages': jobs.pages,
                'per_page': jobs.per_page,
                'total': jobs.total,
                'has_next': jobs.has_next,
                'has_prev': jobs.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """الحصول على تفاصيل وظيفة محددة"""
    try:
        job = Job.query.get_or_404(job_id)
        job_dict = job.to_dict()
        
        # فحص إذا كانت في المفضلة
        if 'user_id' in session:
            favorite = Favorite.query.filter_by(
                user_id=session['user_id'], 
                job_id=job_id
            ).first()
            job_dict['is_favorite'] = favorite is not None
        else:
            job_dict['is_favorite'] = False
        
        return jsonify({'job': job_dict})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """الحصول على قائمة المفضلة للمستخدم"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        favorites = Favorite.query.filter_by(user_id=session['user_id']).order_by(Favorite.created_at.desc()).all()
        favorites_data = [fav.to_dict() for fav in favorites]
        
        return jsonify({'favorites': favorites_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """إضافة وظيفة للمفضلة"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        
        # التأكد من وجود الوظيفة
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # فحص إذا كانت موجودة بالفعل
        existing = Favorite.query.filter_by(
            user_id=session['user_id'], 
            job_id=job_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Job already in favorites'}), 400
        
        # إضافة للمفضلة
        favorite = Favorite(user_id=session['user_id'], job_id=job_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'message': 'Job added to favorites',
            'favorite': favorite.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/favorites/<int:job_id>', methods=['DELETE'])
def remove_favorite(job_id):
    """إزالة وظيفة من المفضلة"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        favorite = Favorite.query.filter_by(
            user_id=session['user_id'], 
            job_id=job_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favorite not found'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Job removed from favorites'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/categories', methods=['GET'])
def get_categories():
    """الحصول على قائمة التخصصات"""
    try:
        categories = Category.query.all()
        categories_data = [cat.to_dict() for cat in categories]
        
        return jsonify({'categories': categories_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/stats', methods=['GET'])
def get_stats():
    """الحصول على إحصائيات الوظائف"""
    try:
        total_jobs = Job.query.count()
        total_companies = db.session.query(Job.company).distinct().count()
        total_sources = db.session.query(Job.source).distinct().count()
        
        # إحصائيات حسب المصدر
        sources_stats = db.session.query(
            Job.source, 
            db.func.count(Job.id).label('count')
        ).group_by(Job.source).all()
        
        # إحصائيات حسب التخصص
        categories_stats = db.session.query(
            Job.category, 
            db.func.count(Job.id).label('count')
        ).group_by(Job.category).all()
        
        return jsonify({
            'total_jobs': total_jobs,
            'total_companies': total_companies,
            'total_sources': total_sources,
            'sources': [{'name': s[0], 'count': s[1]} for s in sources_stats],
            'categories': [{'name': c[0], 'count': c[1]} for c in categories_stats]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/sync', methods=['POST'])
def sync_jobs():
    """مزامنة الوظائف من ملف JSON"""
    try:
        # قراءة ملف الوظائف
        json_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reliefweb_jobs.json')
        
        if not os.path.exists(json_file):
            return jsonify({'error': 'Jobs file not found'}), 404
        
        with open(json_file, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        synced_count = 0
        
        for job_data in jobs_data:
            # فحص إذا كانت الوظيفة موجودة
            existing_job = Job.query.filter_by(
                title=job_data.get('Job Title'),
                company=job_data.get('Company'),
                link=job_data.get('Link')
            ).first()
            
            if not existing_job:
                # إنشاء وظيفة جديدة
                job = Job(
                    title=job_data.get('Job Title', ''),
                    company=job_data.get('Company', ''),
                    location=job_data.get('Location', ''),
                    description=job_data.get('Description', ''),
                    link=job_data.get('Link', ''),
                    source=job_data.get('Source', 'unknown'),
                    job_type=job_data.get('Job Type', 'دوام كامل'),
                    category=job_data.get('Category', 'متنوع'),
                    date_posted=job_data.get('Date', ''),
                    deadline=job_data.get('Deadline', ''),
                    skills=json.dumps(job_data.get('Skills', []))
                )
                db.session.add(job)
                synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully synced {synced_count} jobs',
            'synced_count': synced_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# Admin routes
@jobs_bp.route('/admin')
def admin_panel():
    """صفحة لوحة التحكم الإدارية"""
    return send_from_directory(current_app.static_folder, 'admin.html')


# Admin routes
@jobs_bp.route('/admin')

def admin_panel_new():
    """صفحة لوحة التحكم الإدارية"""
    return send_from_directory(current_app.static_folder, 'admin.html')

@jobs_bp.route('/admin-stats')
def get_admin_stats():
    """الحصول على إحصائيات النظام للوحة الإدارية"""
    try:
        total_jobs = Job.query.count()
        total_companies = db.session.query(Job.company).distinct().count()
        total_users = User.query.count()
        total_favorites = Favorite.query.count()
        
        return jsonify({
            'total_jobs': total_jobs,
            'total_companies': total_companies,
            'total_users': total_users,
            'total_favorites': total_favorites
        })
    except Exception as e:
        logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@jobs_bp.route('/jobs/clear', methods=['DELETE'])
@auth_manager.login_required
def clear_all_jobs():
    """حذف جميع الوظائف"""
    try:
        # حذف جميع المفضلة أولاً
        Favorite.query.delete()
        # حذف جميع الوظائف
        Job.query.delete()
        db.session.commit()
        
        logger.info("تم حذف جميع الوظائف بنجاح")
        return jsonify({
            'success': True,
            'message': 'تم حذف جميع الوظائف بنجاح'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف الوظائف: {e}")
        return jsonify({'error': 'Failed to clear jobs'}), 500

@jobs_bp.route('/jobs/<job_id>', methods=['DELETE'])
@auth_manager.login_required
def delete_single_job(job_id):
    """حذف وظيفة محددة"""
    try:
        job = Job.query.filter_by(id=job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # حذف المفضلة المرتبطة بهذه الوظيفة
        Favorite.query.filter_by(job_id=job_id).delete()
        # حذف الوظيفة
        db.session.delete(job)
        db.session.commit()
        
        logger.info(f"تم حذف الوظيفة {job_id}")
        return jsonify({
            'success': True,
            'message': 'تم حذف الوظيفة بنجاح'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف الوظيفة {job_id}: {e}")
        return jsonify({'error': 'Failed to delete job'}), 500

