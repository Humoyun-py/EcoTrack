import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eco-track-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database/eco.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False