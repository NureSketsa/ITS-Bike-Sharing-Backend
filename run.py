import os
from app import create_app, db
from app.models.user import User
from app.models.kendaraan import Kendaraan, LogPemeliharaan
from app.models.stasiun import Stasiun
from app.models.transaksi import Transaksi
from app.models.layanan import Layanan, TransaksiLayanan

app = create_app(os.getenv('FLASK_ENV', 'default'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Kendaraan': Kendaraan,
        'LogPemeliharaan': LogPemeliharaan,
        'Stasiun': Stasiun,
        'Transaksi': Transaksi,
        'Layanan': Layanan,
        'TransaksiLayanan': TransaksiLayanan
    }

if __name__ == '__main__':
    app.run(debug=True)