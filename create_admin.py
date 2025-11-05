#!/usr/bin/env python3
"""
Admin foydalanuvchi yaratish skripti
"""

import sys
import os

# Loyiha papkasini qo'shish
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Admin foydalanuvchi yaratish"""
    with app.app_context():
        # Admin mavjudligini tekshirish
        admin = User.query.filter_by(email='admin@ecotrack.uz').first()
        if admin:
            print("❌ Admin foydalanuvchi allaqachon mavjud!")
            return
        
        # Yangi admin yaratish
        admin_user = User(
            name='EcoTrack Admin',
            email='admin@ecotrack.uz',
            password_hash=generate_password_hash('admin123')
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin foydalanuvchi muvaffaqiyatli yaratildi!")
        print("📧 Email: admin@ecotrack.uz")
        print("🔑 Parol: admin123")
        print("⚠️  Iltimos, parolni darrov o'zgartiring!")

if __name__ == '__main__':
    create_admin_user()