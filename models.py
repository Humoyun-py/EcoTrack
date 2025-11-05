from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
import random

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationshiplar
    points = db.relationship('EcoPoint', backref='user', lazy='dynamic')
    badges = db.relationship('Badge', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.name}>'

class EcoPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=db.func.current_date())
    points = db.Column(db.Integer, default=0)
    task_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    
    @staticmethod
    def get_user_total_points(user_id):
        result = db.session.query(db.func.sum(EcoPoint.points)).filter(
            EcoPoint.user_id == user_id
        ).scalar()
        return result if result else 0
    
    @staticmethod
    def get_user_points_by_date(user_id, start_date, end_date):
        return db.session.query(db.func.sum(EcoPoint.points)).filter(
            EcoPoint.user_id == user_id,
            EcoPoint.date >= start_date,
            EcoPoint.date <= end_date
        ).scalar() or 0
    
    def __repr__(self):
        return f'<EcoPoint {self.points} - {self.date}>'

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_description = db.Column(db.String(200))
    earned_date = db.Column(db.Date, default=db.func.current_date())
    badge_icon = db.Column(db.String(50), default='🛡️')
    
    @staticmethod
    def assign_badge(user_id, total_points):
        badges = {
            50: {"name": "Green Starter", "description": "Yashil yo'l boshlovchisi", "icon": "🌱"},
            100: {"name": "Eco Friend", "description": "Tabiat do'sti", "icon": "🤝"},
            200: {"name": "Nature Guardian", "description": "Tabiat himoyachisi", "icon": "🛡️"},
            500: {"name": "Planet Hero", "description": "Sayyora qahramoni", "icon": "🦸"},
            1000: {"name": "Eco Master", "description": "Ekologiya ustasi", "icon": "🏆"}
        }
        
        earned_badge = None
        
        for points, badge_info in badges.items():
            if total_points >= points:
                # Badge allaqachon berilganligini tekshirish
                existing_badge = Badge.query.filter_by(
                    user_id=user_id, 
                    badge_name=badge_info["name"]
                ).first()
                
                if not existing_badge:
                    new_badge = Badge(
                        user_id=user_id,
                        badge_name=badge_info["name"],
                        badge_description=badge_info["description"],
                        badge_icon=badge_info["icon"]
                    )
                    db.session.add(new_badge)
                    db.session.commit()
                    earned_badge = badge_info["name"]
        
        return earned_badge
    
    def __repr__(self):
        return f'<Badge {self.badge_name}>'

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    @staticmethod
    def get_random_tip():
        tips = Tip.query.all()
        return random.choice(tips).text if tips else "Tabiatni seving! 🌍"
    
    @staticmethod
    def get_tips_by_category(category):
        return Tip.query.filter_by(category=category).all()
    
    def __repr__(self):
        return f'<Tip {self.text[:50]}...>'