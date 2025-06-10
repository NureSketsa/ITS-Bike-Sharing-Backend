from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.kendaraan import Kendaraan, LogPemeliharaan
from app.models.user import User

kendaraan_bp = Blueprint('kendaraan', __name__)

@kendaraan_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_kendaraan():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    stasiun_id = request.args.get('stasiun_id', type=int)
    
    query = Kendaraan.query
    
    if status:
        query = query.filter(Kendaraan.status == status)
    if stasiun_id:
        query = query.filter(Kendaraan.stasiun_id == stasiun_id)
    
    kendaraan_list = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'kendaraan': [k.to_dict() for k in kendaraan_list.items],
        'total': kendaraan_list.total,
        'pages': kendaraan_list.pages,
        'current_page': page
    }), 200

@kendaraan_bp.route('/<int:kendaraan_id>', methods=['GET'])
@jwt_required()
def get_kendaraan(kendaraan_id):
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    return jsonify({'kendaraan': kendaraan.to_dict()}), 200

@kendaraan_bp.route('/', methods=['POST'])
@jwt_required()
def create_kendaraan():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json()
    
    kendaraan = Kendaraan(
        merk=data.get('merk'),
        tipe=data.get('tipe'),
        status=data.get('status', 'available'),
        stasiun_id=data.get('stasiun_id')
    )
    
    db.session.add(kendaraan)
    db.session.commit()
    
    return jsonify({
        'message': 'Kendaraan created successfully',
        'kendaraan': kendaraan.to_dict()
    }), 201

@kendaraan_bp.route('/<int:kendaraan_id>', methods=['PUT'])
@jwt_required()
def update_kendaraan(kendaraan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    data = request.get_json()
    
    kendaraan.merk = data.get('merk', kendaraan.merk)
    kendaraan.tipe = data.get('tipe', kendaraan.tipe)
    kendaraan.status = data.get('status', kendaraan.status)
    kendaraan.stasiun_id = data.get('stasiun_id', kendaraan.stasiun_id)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Kendaraan updated successfully',
        'kendaraan': kendaraan.to_dict()
    }), 200

@kendaraan_bp.route('/<int:kendaraan_id>', methods=['DELETE'])
@jwt_required()
def delete_kendaraan(kendaraan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    
    db.session.delete(kendaraan)
    db.session.commit()
    
    return jsonify({'message': 'Kendaraan deleted successfully'}), 200

# Log Pemeliharaan routes
@kendaraan_bp.route('/<int:kendaraan_id>/maintenance', methods=['GET'])
@jwt_required()
def get_maintenance_logs(kendaraan_id):
    logs = LogPemeliharaan.query.filter_by(kendaraan_id=kendaraan_id).all()
    return jsonify({
        'maintenance_logs': [log.to_dict() for log in logs]
    }), 200

@kendaraan_bp.route('/<int:kendaraan_id>/maintenance', methods=['POST'])
@jwt_required()
def create_maintenance_log(kendaraan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    # Check if kendaraan exists
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    
    data = request.get_json()
    
    log = LogPemeliharaan(
        kendaraan_id=kendaraan_id,
        tanggal_pemelihara=data.get('tanggal_pemelihara'),
        deskripsi=data.get('deskripsi'),
        biaya=data.get('biaya')
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Maintenance log created successfully',
        'log': log.to_dict()
    }), 201