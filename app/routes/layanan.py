from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.layanan import Layanan, TransaksiLayanan
from app.models.user import User
from datetime import datetime

layanan_bp = Blueprint('layanan', __name__)

@layanan_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_layanan():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    query = Layanan.query
    
    if active_only:
        query = query.filter(Layanan.aksi == True)
    
    layanan_list = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'layanan': [l.to_dict() for l in layanan_list.items],
        'total': layanan_list.total,
        'pages': layanan_list.pages,
        'current_page': page
    }), 200

@layanan_bp.route('/<int:layanan_id>', methods=['GET'])
@jwt_required()
def get_layanan(layanan_id):
    layanan = Layanan.query.get_or_404(layanan_id)
    return jsonify({'layanan': layanan.to_dict()}), 200

@layanan_bp.route('/', methods=['POST'])
@jwt_required()
def create_layanan():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json()
    
    layanan = Layanan(
        nama_layanan=data.get('nama_layanan'),
        deskripsi=data.get('deskripsi'),
        harga=data.get('harga'),
        biaya_dasar=data.get('biaya_dasar'),
        aksi=data.get('aksi', True)
    )
    
    db.session.add(layanan)
    db.session.commit()
    
    return jsonify({
        'message': 'Layanan created successfully',
        'layanan': layanan.to_dict()
    }), 201

@layanan_bp.route('/<int:layanan_id>', methods=['PUT'])
@jwt_required()
def update_layanan(layanan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    layanan = Layanan.query.get_or_404(layanan_id)
    data = request.get_json()
    
    layanan.nama_layanan = data.get('nama_layanan', layanan.nama_layanan)
    layanan.deskripsi = data.get('deskripsi', layanan.deskripsi)
    layanan.harga = data.get('harga', layanan.harga)
    layanan.biaya_dasar = data.get('biaya_dasar', layanan.biaya_dasar)
    layanan.aksi = data.get('aksi', layanan.aksi)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Layanan updated successfully',
        'layanan': layanan.to_dict()
    }), 200

@layanan_bp.route('/<int:layanan_id>', methods=['DELETE'])
@jwt_required()
def delete_layanan(layanan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    layanan = Layanan.query.get_or_404(layanan_id)
    
    # Check if there are active transactions for this service
    active_transactions = TransaksiLayanan.query.filter_by(
        layanan_id=layanan_id,
        status_layanan='active'
    ).count()
    
    if active_transactions > 0:
        return jsonify({
            'message': 'Cannot delete service with active transactions'
        }), 400
    
    db.session.delete(layanan)
    db.session.commit()
    
    return jsonify({'message': 'Layanan deleted successfully'}), 200

# Transaksi Layanan routes
@layanan_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_layanan_transactions():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    layanan_id = request.args.get('layanan_id', type=int)
    
    query = TransaksiLayanan.query
    
    if status:
        query = query.filter(TransaksiLayanan.status_layanan == status)
    if layanan_id:
        query = query.filter(TransaksiLayanan.layanan_id == layanan_id)
    
    # Admin can see all, users see their own
    if user.role != 'admin':
        # You might need to add user_nrp to TransaksiLayanan model
        # or join with Transaksi table to filter by user
        pass
    
    transaksi_list = query.order_by(TransaksiLayanan.tanggal_layanan.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transaksi_layanan': [t.to_dict() for t in transaksi_list.items],
        'total': transaksi_list.total,
        'pages': transaksi_list.pages,
        'current_page': page
    }), 200

@layanan_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_layanan_transaction():
    current_user_nrp = get_jwt_identity()
    data = request.get_json()
    
    transaksi_id = data.get('transaksi_id')
    layanan_id = data.get('layanan_id')
    
    # Check if layanan exists and is active
    layanan = Layanan.query.get_or_404(layanan_id)
    if not layanan.aksi:
        return jsonify({'message': 'Service is not active'}), 400
    
    # Create transaction layanan
    transaksi_layanan = TransaksiLayanan(
        transaksi_id=transaksi_id,
        layanan_id=layanan_id,
        biaya_aktual=data.get('biaya_aktual', layanan.biaya_dasar),
        status_layanan='pending'
    )
    
    db.session.add(transaksi_layanan)
    db.session.commit()
    
    return jsonify({
        'message': 'Service transaction created successfully',
        'transaksi_layanan': transaksi_layanan.to_dict()
    }), 201

@layanan_bp.route('/transactions/<int:transaksi_layanan_id>', methods=['GET'])
@jwt_required()
def get_layanan_transaction(transaksi_layanan_id):
    transaksi_layanan = TransaksiLayanan.query.get_or_404(transaksi_layanan_id)
    return jsonify({'transaksi_layanan': transaksi_layanan.to_dict()}), 200

@layanan_bp.route('/transactions/<int:transaksi_layanan_id>', methods=['PUT'])
@jwt_required()
def update_layanan_transaction(transaksi_layanan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    transaksi_layanan = TransaksiLayanan.query.get_or_404(transaksi_layanan_id)
    data = request.get_json()
    
    # Admin can update any transaction, users can only update their own
    if user.role != 'admin':
        # Here you might want to check if the transaction belongs to the user
        # This requires joining with the main transaction table
        pass
    
    transaksi_layanan.biaya_aktual = data.get('biaya_aktual', transaksi_layanan.biaya_aktual)
    transaksi_layanan.status_layanan = data.get('status_layanan', transaksi_layanan.status_layanan)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Service transaction updated successfully',
        'transaksi_layanan': transaksi_layanan.to_dict()
    }), 200

@layanan_bp.route('/transactions/<int:transaksi_layanan_id>/complete', methods=['PUT'])
@jwt_required()
def complete_layanan_transaction(transaksi_layanan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    transaksi_layanan = TransaksiLayanan.query.get_or_404(transaksi_layanan_id)
    
    transaksi_layanan.status_layanan = 'completed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Service transaction completed successfully',
        'transaksi_layanan': transaksi_layanan.to_dict()
    }), 200

@layanan_bp.route('/transactions/<int:transaksi_layanan_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_layanan_transaction(transaksi_layanan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    transaksi_layanan = TransaksiLayanan.query.get_or_404(transaksi_layanan_id)
    
    # Check if user can cancel this transaction
    if user.role != 'admin':
        # Add logic to check if user owns this transaction
        pass
    
    if transaksi_layanan.status_layanan == 'completed':
        return jsonify({'message': 'Cannot cancel completed transaction'}), 400
    
    transaksi_layanan.status_layanan = 'cancelled'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Service transaction cancelled successfully',
        'transaksi_layanan': transaksi_layanan.to_dict()
    }), 200

@layanan_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_layanan_stats():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    total_services = Layanan.query.count()
    active_services = Layanan.query.filter_by(aksi=True).count()
    
    total_service_transactions = TransaksiLayanan.query.count()
    pending_service_transactions = TransaksiLayanan.query.filter_by(status_layanan='pending').count()
    completed_service_transactions = TransaksiLayanan.query.filter_by(status_layanan='completed').count()
    
    return jsonify({
        'stats': {
            'total_services': total_services,
            'active_services': active_services,
            'total_service_transactions': total_service_transactions,
            'pending_service_transactions': pending_service_transactions,
            'completed_service_transactions': completed_service_transactions
        }
    }), 200