from app import db
from datetime import datetime

class Layanan(db.Model):
    __tablename__ = 'layanan'
    
    layanan_id = db.Column(db.Integer, primary_key=True)
    nama_layanan = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    biaya_dasar = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Boolean, default=True)
    
    # Relationships
    transaksi_details = db.relationship('TransaksiLayanan', back_populates='layanan')
    
    def to_dict(self):
        return {
            'layanan_id': self.layanan_id,
            'nama_layanan': self.nama_layanan,
            'deskripsi': self.deskripsi,
            'biaya_dasar': float(self.biaya_dasar) if self.biaya_dasar else None,
            'status': self.status
        }

class TransaksiLayanan(db.Model):
    __tablename__ = 'transaksi_layanan'
    
    transaksi_layanan_id = db.Column(db.Integer, primary_key=True)
    transaksi_id = db.Column(db.Integer, db.ForeignKey('transaksi.transaksi_id'), nullable=False)
    layanan_id = db.Column(db.Integer, db.ForeignKey('layanan.layanan_id'), nullable=False)

    # Relationships
    transaksi = db.relationship('Transaksi', back_populates='layanan_details')
    layanan = db.relationship('Layanan', back_populates='transaksi_details')
    
    def to_dict(self):
        return {
            'transaksi_layanan_id': self.transaksi_layanan_id,
            'transaksi_id': self.transaksi_id,
            'layanan_id': self.layanan_id,
        }