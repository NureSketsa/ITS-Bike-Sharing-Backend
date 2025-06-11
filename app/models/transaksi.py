from app import db
from datetime import datetime

class Transaksi(db.Model):
    __tablename__ = 'transaksi'
    
    transaksi_id = db.Column(db.Integer, primary_key=True)
    user_nrp = db.Column(db.String(50), db.ForeignKey('user.nrp'), nullable=False)
    kendaraan_id = db.Column(db.Integer, db.ForeignKey('kendaraan.kendaraan_id'))

    # FIXED: Should reference stasiun table, not user table
    stasiun_ambil_id = db.Column(db.Integer, db.ForeignKey('stasiun.stasiun_id'))
    stasiun_kembali_id = db.Column(db.Integer, db.ForeignKey('stasiun.stasiun_id'))

    waktu_mulai = db.Column(db.DateTime, default=datetime.utcnow)
    waktu_selesai = db.Column(db.DateTime, nullable=True)  # FIXED: Should be nullable
    waktu_pembayaran = db.Column(db.DateTime, nullable=True)  # FIXED: Should be nullable

    status_transaksi = db.Column(db.String(50), default='ONGOING')
    payment_gateway_ref = db.Column(db.String(100))
    
    total_biaya = db.Column(db.Numeric(10, 2))
    deposit_dipegang = db.Column(db.Numeric(10, 2))
    
    # Relationships
    user = db.relationship('User', back_populates='transaksi_list')
    kendaraan = db.relationship('Kendaraan', back_populates='transaksi_list')  # ADDED: Missing relationship
    layanan_details = db.relationship('TransaksiLayanan', back_populates='transaksi', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'transaksi_id': self.transaksi_id,
            'user_nrp': self.user_nrp,
            'kendaraan_id': self.kendaraan_id,
            'stasiun_ambil_id': self.stasiun_ambil_id,
            'stasiun_kembali_id': self.stasiun_kembali_id,
            'waktu_mulai': self.waktu_mulai.isoformat() if self.waktu_mulai else None,
            'waktu_selesai': self.waktu_selesai.isoformat() if self.waktu_selesai else None,
            'waktu_pembayaran': self.waktu_pembayaran.isoformat() if self.waktu_pembayaran else None,
            'status_transaksi': self.status_transaksi,
            'payment_gateway_ref': self.payment_gateway_ref,
            'total_biaya': float(self.total_biaya) if self.total_biaya else None,  # FIXED: Convert to float
            'deposit_dipegang': float(self.deposit_dipegang) if self.deposit_dipegang else None  # FIXED: Convert to float
        }   