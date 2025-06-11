from app import db
from datetime import datetime

class Kendaraan(db.Model):
    __tablename__ = 'kendaraan'
    
    kendaraan_id = db.Column(db.Integer, primary_key=True)
    merk = db.Column(db.String(50))
    tipe = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Tersedia')
    stasiun_id = db.Column(db.Integer, db.ForeignKey('stasiun.stasiun_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - FIXED
    transaksi_list = db.relationship('Transaksi', back_populates='kendaraan', lazy=True)
    stasiun = db.relationship('Stasiun', back_populates='kendaraan_list')  # ADDED: Missing relationship
    log_laporan_list = db.relationship('LogLaporan', backref='kendaraan_ref', lazy=True)  # ADDED: Missing relationship
    
    def to_dict(self):
        return {
            'kendaraan_id': self.kendaraan_id,
            'merk': self.merk,
            'tipe': self.tipe,
            'status': self.status,
            'stasiun_id': self.stasiun_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LogLaporan(db.Model):
    __tablename__ = 'log_laporan'
    
    log_laporan_id = db.Column(db.Integer, primary_key=True)
    kendaraan_id = db.Column(db.Integer, db.ForeignKey('kendaraan.kendaraan_id'), nullable=False)
    nrp = db.Column(db.String(50), db.ForeignKey('user.nrp'), nullable=False)

    tanggal_laporan = db.Column(db.DateTime, default=datetime.utcnow)
    laporan = db.Column(db.Text)

    tanggal_pemeliharaan = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Dilaporkan')

    # ADDED: Missing relationships
    user = db.relationship('User', backref='log_laporan_list', lazy=True)
    
    def to_dict(self):
        return {
            'log_laporan_id': self.log_laporan_id,
            'kendaraan_id': self.kendaraan_id,
            'nrp': self.nrp,
            'tanggal_laporan': self.tanggal_laporan.isoformat() if self.tanggal_laporan else None,  # FIXED: Use tanggal_laporan instead of created_at
            'laporan': self.laporan,
            'tanggal_pemeliharaan': self.tanggal_pemeliharaan.isoformat() if self.tanggal_pemeliharaan else None,  # FIXED: Convert to isoformat
            'status': self.status,
        }