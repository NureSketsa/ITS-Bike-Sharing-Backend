from app import db
from datetime import datetime

class Stasiun(db.Model):
    __tablename__ = 'stasiun'
    
    stasiun_id = db.Column(db.Integer, primary_key=True)
    nama_stasiun = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Aktif')

    latitude = db.Column(db.Integer)
    longtitude = db.Column(db.Integer)
    
    # Relationships - FIXED
    kendaraan_list = db.relationship('Kendaraan', back_populates='stasiun', lazy=True)
    
    def to_dict(self):
        return {
            'stasiun_id': self.stasiun_id,
            'nama_stasiun': self.nama_stasiun,
            'alamat': self.alamat,
            'status': self.status,
            'latitude': self.latitude,
            'longtitude': self.longtitude,
        }