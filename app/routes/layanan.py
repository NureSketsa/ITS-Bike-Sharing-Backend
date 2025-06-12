# app/routes/layanan.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.layanan import Layanan, TransaksiLayanan
from app.models.user import User

# Buat blueprint baru untuk layanan
layanan_bp = Blueprint('layanan', __name__)

# Route untuk mendapatkan semua layanan (yang aktif)
@layanan_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_layanan():
    try:
        # Asumsi model Layanan punya kolom 'status' (boolean) untuk menandakan aktif/tidak
        # Jika tidak ada, hapus .filter_by(status=True)
        layanan_list = Layanan.query.filter_by(status=True).all()
        
        return jsonify({
            'success': True,
            'data': [l.to_dict() for l in layanan_list]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to fetch services', 'details': str(e)}), 500

# Route untuk membuat layanan baru (hanya admin)
@layanan_bp.route('/', methods=['POST'])
@jwt_required()
def create_layanan():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()

    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    if not data or not data.get('nama_layanan') or 'harga' not in data:
        return jsonify({'error': 'Missing required fields: nama_layanan, harga'}), 400

    try:
        new_layanan = Layanan(
            nama_layanan=data.get('nama_layanan'),
            deskripsi=data.get('deskripsi'),
            harga=data.get('harga'),
            biaya_dasar=data.get('biaya_dasar', 0),
            status=data.get('status', True)
        )
        db.session.add(new_layanan)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Service created successfully',
            'data': new_layanan.to_dict()
        }), 201
    except Exception as e:
        return handle_error(e, "Failed to create service")
        
# Route untuk menambahkan service ke transaksi yang sudah ada
@layanan_bp.route('/transactions', methods=['POST'])
@jwt_required()
def add_service_to_transaction():
    data = request.get_json()
    transaksi_id = data.get('transaksi_id')
    layanan_id = data.get('layanan_id')

    if not transaksi_id or not layanan_id:
        return jsonify({'error': 'transaksi_id and layanan_id are required'}), 400

    try:
        # Di sini Anda bisa menambahkan validasi lebih lanjut
        # Misalnya, cek apakah transaksi dan layanan ada
        transaksi_layanan = TransaksiLayanan(
            transaksi_id=transaksi_id,
            layanan_id=layanan_id
        )
        db.session.add(transaksi_layanan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Service added to transaction'}), 201
    except Exception as e:
        return handle_error(e, "Failed to add service to transaction")

def handle_error(e, message="An error occurred"):
    # Fungsi helper untuk error, bisa disesuaikan
    print(f"Error in layanan blueprint: {str(e)}")
    db.session.rollback()
    return jsonify({'error': message, 'details': str(e)}), 500