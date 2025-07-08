from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """نموذج المستخدم مع دعم Google OAuth"""
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # علاقة مع المفضلة
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin
        }

class Job(db.Model):
    """نموذج الوظيفة"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    source = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    date_posted = db.Column(db.String(20))
    deadline = db.Column(db.String(20))
    skills = db.Column(db.Text)  # JSON string للمهارات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # علاقة مع المفضلة
    favorites = db.relationship('Favorite', backref='job', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'link': self.link,
            'source': self.source,
            'job_type': self.job_type,
            'category': self.category,
            'date_posted': self.date_posted,
            'deadline': self.deadline,
            'skills': self.skills,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Favorite(db.Model):
    """نموذج المفضلة"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # فهرس مركب لمنع التكرار
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_favorite'),)

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Job:{self.job_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'job': self.job.to_dict() if self.job else None
        }

class Category(db.Model):
    """نموذج التخصصات"""
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name_ar}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
