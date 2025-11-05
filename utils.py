from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import random

def calculate_user_level(total_points):
    """Foydalanuvchi darajasini hisoblash"""
    return total_points // 100

def get_next_level_points(total_points):
    """Keyingi darajaga qancha ball qolganligini hisoblash"""
    current_level = calculate_user_level(total_points)
    next_level_points = (current_level + 1) * 100
    return next_level_points - total_points

def get_progress_percentage(total_points):
    """Progress foizini hisoblash"""
    level_points = total_points % 100
    return level_points

def format_date(dt):
    """Sana formatlash"""
    return dt.strftime("%Y-%m-%d")

def get_daily_tasks():
    """Kunlik topshiriqlar ro'yxati"""
    return [
        {"id": 1, "name": "Plastikdan foydalanmang", "points": 10, "icon": "🚫"},
        {"id": 2, "name": "Suvni tejang", "points": 15, "icon": "💧"},
        {"id": 3, "name": "Eneriyani tejang", "points": 12, "icon": "⚡"},
        {"id": 4, "name": "Qayta ishlang", "points": 20, "icon": "♻️"},
        {"id": 5, "name": "O'simlik ekish", "points": 25, "icon": "🌱"}
    ]

def get_badge_info(total_points):
    """Foydalanuvchi badge ma'lumotlari"""
    badges = [
        {"points": 0, "name": "Boshlovchi", "description": "Yo'l boshida"},
        {"points": 50, "name": "Green Starter", "description": "Yashil yo'l boshlovchisi"},
        {"points": 100, "name": "Eco Friend", "description": "Tabiat do'sti"},
        {"points": 200, "name": "Nature Guardian", "description": "Tabiat himoyachisi"},
        {"points": 500, "name": "Planet Hero", "description": "Sayyora qahramoni"},
        {"points": 1000, "name": "Eco Master", "description": "Ekologiya ustasi"}
    ]
    
    current_badge = badges[0]
    next_badge = badges[1]
    
    for i, badge in enumerate(badges):
        if total_points >= badge['points']:
            current_badge = badge
            if i + 1 < len(badges):
                next_badge = badges[i + 1]
    
    return {
        'current': current_badge,
        'next': next_badge,
        'progress_to_next': total_points - current_badge['points'],
        'needed_for_next': next_badge['points'] - current_badge['points']
    }

def get_weekly_stats(user_id):
    """Haftalik statistikani olish"""
    from models import EcoPoint, db
    from datetime import datetime, timedelta
    
    week_ago = datetime.now() - timedelta(days=7)
    
    weekly_points = db.session.query(db.func.sum(EcoPoint.points)).filter(
        EcoPoint.user_id == user_id,
        EcoPoint.date >= week_ago
    ).scalar() or 0
    
    return {
        'weekly_points': weekly_points,
        'tasks_completed': db.session.query(EcoPoint).filter(
            EcoPoint.user_id == user_id,
            EcoPoint.date >= week_ago
        ).count()
    }

def calculate_co2_saved(points):
    """Ballar asosida saqlangan CO2 miqdorini hisoblash"""
    # Har 10 ball taxminan 1kg CO2 tejashga teng deb hisoblaymiz
    return round(points / 10, 2)

def get_environmental_impact(points):
    """Atrof-muhitga ijobiy ta'sir ma'lumotlari"""
    co2_saved = calculate_co2_saved(points)
    trees_equivalent = round(co2_saved / 21.77, 2)  # 1 daraxt yiliga 21.77kg CO2 yutadi
    km_driven_equivalent = round(co2_saved / 0.404, 2)  # 1 km yo'l = 0.404kg CO2
    
    return {
        'co2_saved': co2_saved,
        'trees_equivalent': trees_equivalent,
        'km_driven_equivalent': km_driven_equivalent
    }