from app import db
from datetime import datetime

class Kendaraan(db.Model):
    __tablename__ = 'kendaraan'
    
    kendaraan_id = db.Column(db.Integer, primary_key=True)
    merk = db.Column(db.String(50))
    tipe = db.Column(db.String(50))
    status = db.Column(db.String(50), default='available')
    stasiun_id = db.Column(db.Integer, db.ForeignKey('stasiun.stasiun_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transaksi_list = db.relationship('Transaksi', backref='kendaraan_ref', lazy=True)
    
    def to_dict(self):
        return {
            'kendaraan_id': self.kendaraan_id,
            'merk': self.merk,
            'tipe': self.tipe,
            'status': self.status,
            'stasiun_id': self.stasiun_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LogPemeliharaan(db.Model):
    __tablename__ = 'log_pemeliharaan'
    
    log_pemeliharaan_id = db.Column(db.Integer, primary_key=True)
    kendaraan_id = db.Column(db.Integer, db.ForeignKey('kendaraan.kendaraan_id'), nullable=False)
    tanggal_pemelihara = db.Column(db.Integer)  # Keeping as int as per your PDM
    deskripsi = db.Column(db.Text)
    biaya = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'log_pemeliharaan_id': self.log_pemeliharaan_id,
            'kendaraan_id': self.kendaraan_id,
            'tanggal_pemelihara': self.tanggal_pemelihara,
            'deskripsi': self.deskripsi,
            'biaya': self.biaya
        }