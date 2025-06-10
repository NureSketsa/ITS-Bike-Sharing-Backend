from app import db
from datetime import datetime

class Layanan(db.Model):
    __tablename__ = 'layanan'
    
    layanan_id = db.Column(db.Integer, primary_key=True)
    nama_layanan = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    harga = db.Column(db.Numeric(10, 2))
    biaya_dasar = db.Column(db.Numeric(10, 2))
    aksi = db.Column(db.Boolean, default=True)
    
    # Relationships
    #transaksi_layanan_list = db.relationship('TransaksiLayanan', backref='layanan_ref', lazy=True)
    transaksi_details = db.relationship('TransaksiLayanan', back_populates='layanan')
    
    def to_dict(self):
        return {
            'layanan_id': self.layanan_id,
            'nama_layanan': self.nama_layanan,
            'deskripsi': self.deskripsi,
            'harga': float(self.harga) if self.harga else None,
            'biaya_dasar': float(self.biaya_dasar) if self.biaya_dasar else None,
            'aksi': self.aksi
        }

class TransaksiLayanan(db.Model):
    __tablename__ = 'transaksi_layanan'
    
    transaksi_layanan_id = db.Column(db.Integer, primary_key=True)
    #transaksi_id = db.Column(db.Integer, nullable=False)
    transaksi_id = db.Column(db.Integer, db.ForeignKey('transaksi.transaksi_id'), nullable=False)
    layanan_id = db.Column(db.Integer, db.ForeignKey('layanan.layanan_id'), nullable=False)
    tanggal_layanan = db.Column(db.DateTime, default=datetime.utcnow)
    biaya_aktual = db.Column(db.Numeric(10, 2))
    status_layanan = db.Column(db.String(50), default='pending')

    transaksi = db.relationship('Transaksi', back_populates='layanan_details')
    layanan = db.relationship('Layanan', back_populates='transaksi_details')
    
    def to_dict(self):
        return {
            'transaksi_layanan_id': self.transaksi_layanan_id,
            'transaksi_id': self.transaksi_id,
            'layanan_id': self.layanan_id,
            'tanggal_layanan': self.tanggal_layanan.isoformat() if self.tanggal_layanan else None,
            'biaya_aktual': float(self.biaya_aktual) if self.biaya_aktual else None,
            'status_layanan': self.status_layanan
        }