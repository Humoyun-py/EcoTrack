#!/usr/bin/env python3
"""
EcoTrack ilovasini ishga tushirish fayli
"""

from app import app, init_db

if __name__ == '__main__':
    print("🌿 EcoTrack ilovasi ishga tushmoqda...")
    print("📍 Manzil: http://127.0.0.1:5000")
    print("⏹ To'xtatish uchun Ctrl+C tugmasini bosing")
    
    try:
        init_db()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 EcoTrack ilovasi to'xtatildi!")
    except Exception as e:
        print(f"❌ Xatolik yuz berdi: {e}")