from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200))
    bangdan_name = db.Column(db.String(100))
    ranking = db.Column(db.Integer, default=0)
    subject = db.Column(db.String(500))
    price = db.Column(db.Float)
    unit = db.Column(db.String(50))
    chengjiaov = db.Column(db.Float)   # 清洗后统一为万元
    saleVolume = db.Column(db.Integer, default=0)
    odUrl = db.Column(db.String(500))
    category = db.Column(db.String(50))  # BBQ, DownJacket, Year
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.subject[:20]}>'