from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.transaksi import Transaksi
from app.models.kendaraan import Kendaraan
from app.models.stasiun import Stasiun
from app.models.user import User
from datetime import datetime
import uuid

transaksi_bp = Blueprint('transaksi', __name__)



@transaksi_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Rute tes di transaksi.py BERHASIL!"})


@transaksi_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_transaksi():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    # Admin can see all transactions, users only see their own
    if user.role == 'admin':
        query = Transaksi.query
    else:
        query = Transaksi.query.filter_by(user_nrp=current_user_nrp)
    
    if status:
        query = query.filter(Transaksi.status_transaksi == status)
    
    transaksi_list = query.order_by(Transaksi.tanggal_pinjam.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transaksi': [t.to_dict() for t in transaksi_list.items],
        'total': transaksi_list.total,
        'pages': transaksi_list.pages,
        'current_page': page
    }), 200

@transaksi_bp.route('/<int:transaksi_id>', methods=['GET'])
@jwt_required()
def get_transaksi(transaksi_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    
    # Check if user can access this transaction
    if user.role != 'admin' and transaksi.user_nrp != current_user_nrp:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({'transaksi': transaksi.to_dict()}), 200

# Kembalikan seperti semula
@transaksi_bp.route('/rent', methods=['POST'])
@jwt_required()
def rent_bike():
    current_user_nrp = get_jwt_identity()
    data = request.get_json()
    
    kendaraan_id = data.get('kendaraan_id')
    stasiun_ambil_id = data.get('stasiun_ambil_id')
    
    # Check if user has active rental
    active_rental = Transaksi.query.filter_by(
        user_nrp=current_user_nrp,
        status_transaksi='active'
    ).first()
    
    if active_rental:
        return jsonify({'message': 'You already have an active rental'}), 400
    
    # Check if bike is available
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    if kendaraan.status != 'available':
        return jsonify({'message': 'Bike is not available'}), 400
    
    # Check if bike is at the specified station
    if kendaraan.stasiun_id != stasiun_ambil_id:
        return jsonify({'message': 'Bike is not at the specified station'}), 400
    
    # Create transaction
    transaksi = Transaksi(
        user_nrp=current_user_nrp,
        kendaraan_id=kendaraan_id,
        stasiun_ambil_id=stasiun_ambil_id,
        reference_number=str(uuid.uuid4())[:8].upper(),
        status_transaksi='active'
    )
    
    # Update bike status
    kendaraan.status = 'rented'
    kendaraan.stasiun_id = None
    
    db.session.add(transaksi)
    db.session.commit()
    
    return jsonify({
        'message': 'Bike rented successfully',
        'transaksi': transaksi.to_dict()
    }), 201

@transaksi_bp.route('/return', methods=['POST'])
@jwt_required()
def return_bike():
    current_user_nrp = get_jwt_identity()
    data = request.get_json()
    
    transaksi_id = data.get('transaksi_id')
    stasiun_kembali_id = data.get('stasiun_kembali_id')
    
    # Get active transaction
    transaksi = Transaksi.query.filter_by(
        transaksi_id=transaksi_id,
        user_nrp=current_user_nrp,
        status_transaksi='active'
    ).first()
    
    if not transaksi:
        return jsonify({'message': 'Active transaction not found'}), 404
    
    # Check if return station exists
    stasiun = Stasiun.query.get_or_404(stasiun_kembali_id)
    
    # Update transaction
    transaksi.stasiun_kembali_id = stasiun_kembali_id
    transaksi.waktu_kembali = datetime.utcnow()
    transaksi.status_transaksi = 'completed'
    
    # Update bike status and location
    kendaraan = Kendaraan.query.get(transaksi.kendaraan_id)
    kendaraan.status = 'available'
    kendaraan.stasiun_id = stasiun_kembali_id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Bike returned successfully',
        'transaksi': transaksi.to_dict()
    }), 200

@transaksi_bp.route('/<int:transaksi_id>/complete', methods=['PUT'])
@jwt_required()
def complete_transaksi(transaksi_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    
    # Check access rights
    if user.role != 'admin' and transaksi.user_nrp != current_user_nrp:
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    
    transaksi.waktu_selesai = datetime.utcnow()
    transaksi.waktu_pembayaran = datetime.utcnow()
    transaksi.status_transaksi = 'paid'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction completed successfully',
        'transaksi': transaksi.to_dict()
    }), 200

@transaksi_bp.route('/my-rentals', methods=['GET'])
@jwt_required()
def get_my_rentals():
    current_user_nrp = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    transaksi_list = Transaksi.query.filter_by(
        user_nrp=current_user_nrp
    ).order_by(Transaksi.tanggal_pinjam.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'rentals': [t.to_dict() for t in transaksi_list.items],
        'total': transaksi_list.total,
        'pages': transaksi_list.pages,
        'current_page': page
    }), 200

@transaksi_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_rental():
    current_user_nrp = get_jwt_identity()
    
    active_rental = Transaksi.query.filter_by(
        user_nrp=current_user_nrp,
        status_transaksi='active'
    ).first()
    
    if active_rental:
        return jsonify({'active_rental': active_rental.to_dict()}), 200
    else:
        return jsonify({'active_rental': None}), 200

@transaksi_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_transaction_stats():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    total_transactions = Transaksi.query.count()
    active_transactions = Transaksi.query.filter_by(status_transaksi='active').count()
    completed_transactions = Transaksi.query.filter_by(status_transaksi='completed').count()
    paid_transactions = Transaksi.query.filter_by(status_transaksi='paid').count()
    
    return jsonify({
        'stats': {
            'total_transactions': total_transactions,
            'active_transactions': active_transactions,
            'completed_transactions': completed_transactions,
            'paid_transactions': paid_transactions
        }
    }), 200