from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    
    nrp = db.Column(db.String(50), primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    no_hp = db.Column(db.String(20))
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transaksi_list = db.relationship('Transaksi', back_populates='user', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'nrp': self.nrp,
            'nama': self.nama,
            'email': self.email,
            'no_hp': self.no_hp,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }