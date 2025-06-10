from .auth import auth_bp
from .kendaraan import kendaraan_bp
from .stasiun import stasiun_bp
from .transaksi import transaksi_bp
from .layanan import layanan_bp

__all__ = [
    'auth_bp',
    'kendaraan_bp',
    'stasiun_bp',
    'transaksi_bp',
    'layanan_bp'
]