from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os

# Database initialization
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name}>'

class EcoPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    task_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    
    @staticmethod
    def get_user_total_points(user_id):
        result = db.session.query(db.func.sum(EcoPoint.points)).filter(
            EcoPoint.user_id == user_id
        ).scalar()
        return result if result else 0
    
    def __repr__(self):
        return f'<EcoPoint {self.points} - {self.date}>'

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_description = db.Column(db.String(200))
    earned_date = db.Column(db.Date, default=datetime.utcnow)
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

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_random_tip():
        tips = Tip.query.all()
        return random.choice(tips).text if tips else "Tabiatni seving! 🌍"

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eco-track-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Iltimos, tizimga kiring!'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add initial tips if empty
        if Tip.query.count() == 0:
            tips_data = [
                {"text": "Bugun plastik ishlatmang 🌿", "category": "daily"},
                {"text": "Daraxt eking 🌳", "category": "action"},
                {"text": "Yorug'likni tejang 💡", "category": "energy"},
                {"text": "Suvni tejang 💧", "category": "water"},
                {"text": "Qayta ishlang ♻️", "category": "recycle"},
                {"text": "Velosiped haydang 🚲", "category": "transport"},
                {"text": "Mahalliy mahsulotlar sotib oling 🍎", "category": "shopping"},
                {"text": "Kompost qiling 🍂", "category": "waste"},
            ]
            
            for tip_info in tips_data:
                tip = Tip(text=tip_info["text"], category=tip_info["category"])
                db.session.add(tip)
            
            db.session.commit()
            print("✅ Database initialized with sample data")

def calculate_environmental_impact(points):
    """Calculate environmental impact based on points"""
    return {
        'co2_saved': round(points * 0.2, 1),
        'water_saved': points * 1.5,
        'plastic_saved': round(points * 0.1, 1),
        'energy_saved': points * 0.5
    }

def get_impact_comparisons(impact):
    """Get environmental impact comparisons"""
    return {
        'co2_car_km': round(impact['co2_saved'] / 0.404, 1) if impact['co2_saved'] > 0 else 0,
        'water_showers': round(impact['water_saved'] / 65) if impact['water_saved'] > 0 else 0,
        'plastic_bottles': round(impact['plastic_saved'] / 0.05) if impact['plastic_saved'] > 0 else 0,
        'energy_homes': round(impact['energy_saved'] / 30) if impact['energy_saved'] > 0 else 0
    }

def get_next_badge_info(total_points):
    """Get information about the next badge to earn"""
    badges = [
        {"points": 50, "name": "Green Starter", "description": "Yashil yo'l boshlovchisi", "icon": "🌱"},
        {"points": 100, "name": "Eco Friend", "description": "Tabiat do'sti", "icon": "🤝"},
        {"points": 200, "name": "Nature Guardian", "description": "Tabiat himoyachisi", "icon": "🛡️"},
        {"points": 500, "name": "Planet Hero", "description": "Sayyora qahramoni", "icon": "🦸"},
        {"points": 1000, "name": "Eco Master", "description": "Ekologiya ustasi", "icon": "🏆"}
    ]
    
    # Find current and next badge
    current_badge = badges[0]
    next_badge = badges[1] if len(badges) > 1 else badges[0]
    
    for i, badge in enumerate(badges):
        if total_points >= badge['points']:
            current_badge = badge
            if i + 1 < len(badges):
                next_badge = badges[i + 1]
            else:
                # If it's the last badge, show current one as next (completed)
                next_badge = badge
    
    # Calculate progress to next badge
    progress = 0
    if next_badge['points'] > current_badge['points']:
        progress = ((total_points - current_badge['points']) / 
                   (next_badge['points'] - current_badge['points'])) * 100
    else:
        progress = 100  # All badges earned
    
    return {
        'name': next_badge['name'],
        'description': next_badge['description'],
        'icon': next_badge['icon'],
        'current': total_points,
        'required': next_badge['points'],
        'progress': min(100, progress)
    }

# Routes
@app.route('/')
def index():
    # Basic statistics
    total_users = User.query.count() or 0
    total_tasks = EcoPoint.query.count() or 0
    total_co2 = total_tasks * 2
    
    # User stats if logged in
    user_stats = {}
    if current_user.is_authenticated:
        total_points = EcoPoint.get_user_total_points(current_user.id)
        user_level = total_points // 100
        
        # Today's tasks
        today = datetime.now().date()
        today_points = EcoPoint.query.filter_by(
            user_id=current_user.id, 
            date=today
        ).with_entities(db.func.sum(EcoPoint.points)).scalar() or 0
        
        # Recent badges
        recent_badges = Badge.query.filter_by(
            user_id=current_user.id
        ).order_by(Badge.earned_date.desc()).limit(3).all()
        
        user_stats = {
            'total_points': total_points,
            'level': user_level,
            'badges_count': Badge.query.filter_by(user_id=current_user.id).count(),
            'today_points': today_points,
            'recent_badges': recent_badges,
            'today_co2': round(today_points * 0.2, 1),
            'today_water': int(today_points * 1.5),
            'today_plastic': round(today_points * 0.1, 1)
        }
    
    # Community statistics
    total_co2_saved = total_tasks * 2
    total_water_saved = total_tasks * 15
    total_trees = total_co2_saved // 21 if total_co2_saved > 0 else 0
    active_days = 30
    
    return render_template('index.html',
                         total_users=total_users,
                         total_tasks=total_tasks,
                         total_co2=total_co2,
                         user_stats=user_stats,
                         total_co2_saved=total_co2_saved,
                         total_water_saved=total_water_saved,
                         total_trees=total_trees,
                         active_days=active_days,
                         now=datetime.now())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validation
            if not name or not email or not password:
                flash('Barcha maydonlarni to\'ldiring', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Parol kamida 6 ta belgidan iborat bo\'lishi kerak', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Bu email allaqachon ro\'yxatdan o\'tgan', 'error')
                return redirect(url_for('register'))
            
            # Create user
            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password_hash=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Auto login
            login_user(new_user)
            flash(f'Muvaffaqiyatli ro\'yxatdan o\'tdingiz! Xush kelibsiz, {name}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ro\'yxatdan o\'tishda xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Xush kelibsiz, {user.name}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Email yoki parol noto\'g\'ri', 'error')
                
        except Exception as e:
            flash('Kirishda xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Daily tasks
    daily_tasks = [
        {"id": 1, "name": "Plastikdan foydalanmang", "points": 10, "icon": "🚫"},
        {"id": 2, "name": "Suvni tejang", "points": 15, "icon": "💧"},
        {"id": 3, "name": "Eneriyani tejang", "points": 12, "icon": "⚡"},
        {"id": 4, "name": "Qayta ishlang", "points": 20, "icon": "♻️"},
        {"id": 5, "name": "O'simlik ekish", "points": 25, "icon": "🌱"}
    ]
    
    # User statistics
    total_points = EcoPoint.get_user_total_points(current_user.id)
    user_level = total_points // 100
    next_level_points = (user_level + 1) * 100 - total_points
    
    # Weekly statistics
    week_ago = datetime.now() - timedelta(days=7)
    weekly_points = EcoPoint.query.filter(
        EcoPoint.user_id == current_user.id,
        EcoPoint.date >= week_ago.date()
    ).with_entities(db.func.sum(EcoPoint.points)).scalar() or 0
    
    weekly_tasks = EcoPoint.query.filter(
        EcoPoint.user_id == current_user.id,
        EcoPoint.date >= week_ago.date()
    ).count()
    
    weekly_stats = {
        'weekly_points': weekly_points,
        'tasks_completed': weekly_tasks
    }
    
    # Environmental impact
    environmental_impact = calculate_environmental_impact(total_points)
    
    # Today's completed tasks
    today = datetime.now().date()
    completed_today = EcoPoint.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).all()
    completed_task_ids = [point.task_type for point in completed_today]
    
    # Random tip
    random_tip = Tip.get_random_tip()
    
    return render_template('dashboard.html', 
                         tasks=daily_tasks,
                         total_points=total_points,
                         user_level=user_level,
                         next_level_points=next_level_points,
                         random_tip=random_tip,
                         weekly_stats=weekly_stats,
                         environmental_impact=environmental_impact,
                         completed_task_ids=completed_task_ids,
                         now=datetime.now())

@app.route('/complete_task', methods=['POST'])
@login_required
def complete_task():
    try:
        task_id = request.json.get('task_id')
        task_points = request.json.get('points')
        
        # Check if task already completed today
        today = datetime.now().date()
        existing_task = EcoPoint.query.filter_by(
            user_id=current_user.id,
            date=today,
            task_type=f"task_{task_id}"
        ).first()
        
        if existing_task:
            return jsonify({
                'success': False,
                'message': 'Siz bugun bu topshiriqni allaqachon bajardingiz!'
            })
        
        # Add task completion
        new_point = EcoPoint(
            user_id=current_user.id,
            points=task_points,
            task_type=f"task_{task_id}"
        )
        db.session.add(new_point)
        db.session.commit()
        
        # Check for new badges
        total_points = EcoPoint.get_user_total_points(current_user.id)
        badge_name = Badge.assign_badge(current_user.id, total_points)
        
        return jsonify({
            'success': True,
            'total_points': total_points,
            'badge_earned': badge_name,
            'message': f'Tabriklaymiz! +{task_points} ball qo\'lga kiritdingiz!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.'
        })

@app.route('/profile')
@login_required
def profile():
    try:
        total_points = EcoPoint.get_user_total_points(current_user.id)
        user_level = total_points // 100
        progress_percentage = total_points % 100
        next_level_points = (user_level + 1) * 100 - total_points
        
        # Badges
        badges = Badge.query.filter_by(user_id=current_user.id).order_by(Badge.earned_date.desc()).all()
        
        # Active days
        active_days = db.session.query(db.func.count(db.func.distinct(EcoPoint.date))).filter(
            EcoPoint.user_id == current_user.id
        ).scalar() or 0
        
        # Today's tasks
        today = datetime.now().date()
        today_tasks_db = EcoPoint.query.filter_by(
            user_id=current_user.id,
            date=today
        ).all()
        
        today_tasks = []
        for task in today_tasks_db:
            task_info = {
                'icon': '🌿',
                'name': 'Ekologik topshiriq',
                'time': 'Bugun',
                'points': task.points
            }
            if 'task_1' in task.task_type:
                task_info.update({'icon': '🚫', 'name': 'Plastikdan foydalanmang'})
            elif 'task_2' in task.task_type:
                task_info.update({'icon': '💧', 'name': 'Suvni tejang'})
            elif 'task_3' in task.task_type:
                task_info.update({'icon': '⚡', 'name': 'Eneriyani tejang'})
            elif 'task_4' in task.task_type:
                task_info.update({'icon': '♻️', 'name': 'Qayta ishlang'})
            elif 'task_5' in task.task_type:
                task_info.update({'icon': '🌱', 'name': 'O\'simlik ekish'})
            
            today_tasks.append(task_info)
        
        # Today's points
        today_points = sum(task.points for task in today_tasks_db)
        
        # Today's environmental impact
        today_impact = calculate_environmental_impact(today_points)
        today_comparisons = get_impact_comparisons(today_impact)
        
        # Recent activities
        recent_activities = []
        activities_db = EcoPoint.query.filter_by(
            user_id=current_user.id
        ).order_by(EcoPoint.date.desc()).limit(10).all()
        
        for activity in activities_db:
            activity_info = {
                'date': activity.date,
                'icon': '✅',
                'description': 'Ekologik topshiriq bajarildi',
                'points': activity.points
            }
            if 'task_1' in activity.task_type:
                activity_info.update({'icon': '🚫', 'description': 'Plastikdan foydalanmadingiz'})
            elif 'task_2' in activity.task_type:
                activity_info.update({'icon': '💧', 'description': 'Suv tejadingiz'})
            elif 'task_3' in activity.task_type:
                activity_info.update({'icon': '⚡', 'description': 'Eneriya tejadingiz'})
            elif 'task_4' in activity.task_type:
                activity_info.update({'icon': '♻️', 'description': 'Chiqlarni qayta ishladingiz'})
            elif 'task_5' in activity.task_type:
                activity_info.update({'icon': '🌱', 'description': 'O\'simlik ekdingiz'})
            
            recent_activities.append(activity_info)
        
        # Total environmental impact
        total_impact = calculate_environmental_impact(total_points)
        total_comparisons = get_impact_comparisons(total_impact)
        
        # Next badge info
        next_badge = get_next_badge_info(total_points)
        
        # Last activity
        last_activity = "Bugun"
        if recent_activities:
            last_activity_date = recent_activities[0]['date']
            if last_activity_date == datetime.now().date():
                last_activity = "Bugun"
            else:
                days_ago = (datetime.now().date() - last_activity_date).days
                last_activity = f"{days_ago} kun oldin"
        
        return render_template('profile.html',
                             user=current_user,
                             total_points=total_points,
                             user_level=user_level,
                             progress_percentage=progress_percentage,
                             next_level_points=next_level_points,
                             badges=badges,
                             active_days=active_days,
                             today_date=datetime.now().strftime('%Y-%m-%d'),
                             today_tasks=today_tasks,
                             today_points=today_points,
                             today_co2=today_impact['co2_saved'],
                             today_water=int(today_impact['water_saved']),
                             today_plastic=today_impact['plastic_saved'],
                             co2_car_km=today_comparisons['co2_car_km'],
                             water_showers=today_comparisons['water_showers'],
                             plastic_bottles=today_comparisons['plastic_bottles'],
                             recent_activities=recent_activities,
                             total_co2_saved=total_impact['co2_saved'],
                             total_water_saved=int(total_impact['water_saved']),
                             total_plastic_saved=total_impact['plastic_saved'],
                             total_energy_saved=int(total_impact['energy_saved']),
                             total_co2_trees=round(total_impact['co2_saved'] / 21) if total_impact['co2_saved'] > 0 else 0,
                             total_water_showers=round(total_impact['water_saved'] / 65) if total_impact['water_saved'] > 0 else 0,
                             total_plastic_bottles=round(total_impact['plastic_saved'] / 0.05) if total_impact['plastic_saved'] > 0 else 0,
                             total_energy_homes=round(total_impact['energy_saved'] / 30) if total_impact['energy_saved'] > 0 else 0,
                             next_badge=next_badge,
                             last_activity=last_activity)
                             
    except Exception as e:
        print(f"Profile error: {str(e)}")
        flash('Profilni yuklashda xatolik yuz berdi', 'error')
        return redirect(url_for('dashboard'))

# YANGI: Stats sahifasi qo'shildi
@app.route('/stats')
@login_required
def stats():
    """Statistika sahifasi"""
    try:
        total_points = EcoPoint.get_user_total_points(current_user.id)
        user_level = total_points // 100
        
        # Haftalik statistikalar
        week_ago = datetime.now() - timedelta(days=7)
        weekly_points = EcoPoint.query.filter(
            EcoPoint.user_id == current_user.id,
            EcoPoint.date >= week_ago.date()
        ).with_entities(db.func.sum(EcoPoint.points)).scalar() or 0
        
        weekly_tasks = EcoPoint.query.filter(
            EcoPoint.user_id == current_user.id,
            EcoPoint.date >= week_ago.date()
        ).count()
        
        weekly_stats = {
            'weekly_points': weekly_points,
            'tasks_completed': weekly_tasks
        }
        
        # Atrof-muhitga ta'sir
        environmental_impact = calculate_environmental_impact(total_points)
        
        # Yutuqlar
        badges = Badge.query.filter_by(user_id=current_user.id).all()
        
        return render_template('stats.html',
                             total_points=total_points,
                             user_level=user_level,
                             weekly_stats=weekly_stats,
                             environmental_impact=environmental_impact,
                             badges=badges)
                             
    except Exception as e:
        print(f"Stats error: {str(e)}")
        flash('Statistikani yuklashda xatolik yuz berdi', 'error')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Siz tizimdan muvaffaqiyatli chiqdingiz', 'info')
    return redirect(url_for('index'))

@app.route('/get_tip')
@login_required
def get_tip():
    random_tip = Tip.get_random_tip()
    return jsonify({'tip': random_tip})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("🌿 EcoTrack ilovasi ishga tushmoqda...")
    print("📍 Manzil: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)