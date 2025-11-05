from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
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
    is_admin = db.Column(db.Boolean, default=False)
    
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

# Blog Modellari
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    
    author = db.relationship('User', backref='posts')
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostLike user:{self.user_id} post:{self.post_id}>'

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='comments')
    
    def __repr__(self):
        return f'<PostComment {self.content[:50]}...>'

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

def create_admin_user():
    """Admin foydalanuvchi yaratish"""
    admin_email = "admin@ecotrack.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_password = generate_password_hash("admin123")
        new_admin = User(
            name="EcoTrack Admin",
            email=admin_email,
            password_hash=admin_password,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Admin foydalanuvchi yaratildi: admin@ecotrack.com / admin123")

def init_db():
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Test foydalanuvchi yaratish
        test_user = User.query.filter_by(email="test@test.com").first()
        if not test_user:
            test_password = generate_password_hash("test123")
            new_user = User(
                name="Test User",
                email="test@test.com",
                password_hash=test_password
            )
            db.session.add(new_user)
            db.session.commit()
            print("✅ Test foydalanuvchi yaratildi: test@test.com / test123")
        
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
    return {
        'co2_saved': round(points * 0.2, 1),
        'water_saved': points * 1.5,
        'plastic_saved': round(points * 0.1, 1),
        'energy_saved': points * 0.5
    }

# ===== ASOSIY ROUTELAR =====
@app.route('/')
def index():
    total_users = User.query.count() or 0
    total_tasks = EcoPoint.query.count() or 0
    total_co2 = total_tasks * 2
    
    user_stats = {}
    if current_user.is_authenticated:
        total_points = EcoPoint.get_user_total_points(current_user.id)
        user_level = total_points // 100
        
        today = datetime.now().date()
        today_points = EcoPoint.query.filter_by(
            user_id=current_user.id, 
            date=today
        ).with_entities(db.func.sum(EcoPoint.points)).scalar() or 0
        
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
            
            if not name or not email or not password:
                flash('Barcha maydonlarni to\'ldiring', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Parol kamida 6 ta belgidan iborat bo\'lishi kerak', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Bu email allaqachon ro\'yxatdan o\'tgan', 'error')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password_hash=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
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
    daily_tasks = [
        {"id": 1, "name": "Plastikdan foydalanmang", "points": 10, "icon": "🚫"},
        {"id": 2, "name": "Suvni tejang", "points": 15, "icon": "💧"},
        {"id": 3, "name": "Eneriyani tejang", "points": 12, "icon": "⚡"},
        {"id": 4, "name": "Qayta ishlang", "points": 20, "icon": "♻️"},
        {"id": 5, "name": "O'simlik ekish", "points": 25, "icon": "🌱"}
    ]
    
    total_points = EcoPoint.get_user_total_points(current_user.id)
    user_level = total_points // 100
    next_level_points = (user_level + 1) * 100 - total_points
    
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
    
    environmental_impact = calculate_environmental_impact(total_points)
    
    today = datetime.now().date()
    completed_today = EcoPoint.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).all()
    completed_task_ids = [point.task_type for point in completed_today]
    
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
        
        new_point = EcoPoint(
            user_id=current_user.id,
            points=task_points,
            task_type=f"task_{task_id}"
        )
        db.session.add(new_point)
        db.session.commit()
        
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
        
        badges = Badge.query.filter_by(user_id=current_user.id).order_by(Badge.earned_date.desc()).all()
        
        return render_template('profile.html',
                            user=current_user,
                            total_points=total_points,
                            user_level=user_level,
                            badges=badges)
                             
    except Exception as e:
        print(f"Profile error: {str(e)}")
        flash('Profilni yuklashda xatolik yuz berdi', 'error')
        return redirect(url_for('dashboard'))

@app.route('/stats')
@login_required
def stats():
    try:
        total_points = EcoPoint.get_user_total_points(current_user.id)
        user_level = total_points // 100
        
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
        
        environmental_impact = calculate_environmental_impact(total_points)
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

# ===== BLOG ROUTES =====
@app.route('/blog')
def blog_index():
    try:
        posts = BlogPost.query.filter_by(is_published=True)\
            .order_by(BlogPost.created_at.desc())\
            .all()
        return render_template('blog.html', posts=posts)
    except Exception as e:
        print(f"Blog error: {str(e)}")
        flash('Blog sahifasini yuklashda xatolik', 'error')
        return redirect(url_for('index'))

@app.route('/blog/create', methods=['GET', 'POST'])
@login_required
def blog_create():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            
            if not title or not content:
                flash('Sarlavha va mazumni to\'ldiring', 'error')
                return redirect(url_for('blog_create'))
            
            post = BlogPost(
                title=title,
                content=content,
                author_id=current_user.id
            )
            
            db.session.add(post)
            db.session.commit()
            
            flash('Post muvaffaqiyatli yaratildi!', 'success')
            return redirect(url_for('blog_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Post yaratishda xatolik yuz berdi', 'error')
            return redirect(url_for('blog_create'))
    
    return render_template('blog_create.html')

# ===== ADMIN ROUTES =====
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    # Agar admin allaqachon kirgan bo'lsa, admin paneliga yo'naltirish
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                if user.is_admin:
                    login_user(user)
                    flash(f'Xush kelibsiz, Admin {user.name}!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Sizda admin huquqi yo\'q. Faqat admin foydalanuvchilari kirishi mumkin.', 'error')
            else:
                flash('Email yoki parol noto\'g\'ri', 'error')
                
        except Exception as e:
            print(f"Admin login error: {str(e)}")
            flash('Kirishda xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q', 'error')
        return redirect(url_for('index'))
    
    try:
        # Admin statistikasi
        total_users = User.query.count()
        total_posts = BlogPost.query.count()
        total_comments = PostComment.query.count()
        total_eco_points = EcoPoint.query.count()
        
        stats = {
            'total_users': total_users,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_eco_points': total_eco_points
        }
        
        # So'nggi faolliklar
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
        
        return render_template('admin_dashboard.html', 
                             stats=stats,
                             recent_users=recent_users,
                             recent_posts=recent_posts)
    except Exception as e:
        print(f"Admin dashboard error: {str(e)}")
        flash('Admin panelini yuklashda xatolik', 'error')
        return redirect(url_for('index'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q', 'error')
        return redirect(url_for('index'))
    
    try:
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        print(f"Admin users error: {str(e)}")
        flash('Foydalanuvchilarni yuklashda xatolik', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/posts')
@login_required
def admin_posts():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q', 'error')
        return redirect(url_for('index'))
    
    try:
        posts = BlogPost.query.all()
        return render_template('admin_posts.html', posts=posts)
    except Exception as e:
        print(f"Admin posts error: {str(e)}")
        flash('Postlarni yuklashda xatolik', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/comments')
@login_required
def admin_comments():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q', 'error')
        return redirect(url_for('index'))
    
    try:
        comments = PostComment.query.all()
        return render_template('admin_comments.html', comments=comments)
    except Exception as e:
        print(f"Admin comments error: {str(e)}")
        flash('Kommentlarni yuklashda xatolik', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/eco-points')
@login_required
def admin_eco_points():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q', 'error')
        return redirect(url_for('index'))
    
    try:
        eco_points = EcoPoint.query.all()
        return render_template('admin_eco_points.html', eco_points=eco_points)
    except Exception as e:
        print(f"Admin eco points error: {str(e)}")
        flash('Eco ballarni yuklashda xatolik', 'error')
        return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("🌿 EcoTrack ilovasi ishga tushmoqda...")
    print("📍 Manzil: http://127.0.0.1:5000")
    print("👤 Oddiy foydalanuvchi: test@test.com / test123")
    print("🔐 Admin login: admin@ecotrack.com / admin123")
    print("🔗 Admin panel: http://127.0.0.1:5000/admin-login")
    app.run(debug=True, host='0.0.0.0', port=5000)