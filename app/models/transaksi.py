from app import db
from datetime import datetime

class Transaksi(db.Model):
    __tablename__ = 'transaksi'
    
    transaksi_id = db.Column(db.Integer, primary_key=True)
    user_nrp = db.Column(db.String(50), db.ForeignKey('user.nrp'), nullable=False)
    kendaraan_id = db.Column(db.Integer, db.ForeignKey('kendaraan.kendaraan_id'))
    stasiun_ambil_id = db.Column(db.Integer)
    stasiun_kembali_id = db.Column(db.Integer)
    waktu_selesai = db.Column(db.DateTime)
    tanggal_pinjam = db.Column(db.DateTime, default=datetime.utcnow)
    waktu_kembali = db.Column(db.DateTime)
    waktu_pembayaran = db.Column(db.DateTime)
    status_transaksi = db.Column(db.String(50), default='active')
    reference_number = db.Column(db.String(100))

    user = db.relationship('User', back_populates='transaksi_list')
    layanan_details = db.relationship('TransaksiLayanan', back_populates='transaksi', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'transaksi_id': self.transaksi_id,
            'user_nrp': self.user_nrp,
            'kendaraan_id': self.kendaraan_id,
            'stasiun_ambil_id': self.stasiun_ambil_id,
            'stasiun_kembali_id': self.stasiun_kembali_id,
            'waktu_selesai': self.waktu_selesai.isoformat() if self.waktu_selesai else None,
            'tanggal_pinjam': self.tanggal_pinjam.isoformat() if self.tanggal_pinjam else None,
            'waktu_kembali': self.waktu_kembali.isoformat() if self.waktu_kembali else None,
            'waktu_pembayaran': self.waktu_pembayaran.isoformat() if self.waktu_pembayaran else None,
            'status_transaksi': self.status_transaksi,
            'reference_number': self.reference_number
        }