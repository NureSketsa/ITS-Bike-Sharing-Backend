from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.kendaraan import Kendaraan, LogLaporan  # FIXED: Import LogLaporan instead of LogPemeliharaan
from app.models.user import User
from app.models.stasiun import Stasiun

kendaraan_bp = Blueprint('kendaraan', __name__)

@kendaraan_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_kendaraan():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    stasiun_id = request.args.get('stasiun_id', type=int)

    # =======================================================================
    # Querry Join: mengambil data kendaraan beserta nama stasiun
    query = db.session.query(
        Kendaraan, 
        Stasiun.nama_stasiun.label('stasiun_nama')
    ).join(Stasiun, Kendaraan.stasiun_id == Stasiun.stasiun_id, isouter=True)
    # Nure
    # =======================================================================
    
    if status:
        query = query.filter(Kendaraan.status == status)
    if stasiun_id:
        query = query.filter(Kendaraan.stasiun_id == stasiun_id)

    

    kendaraan_list = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    results = []
    for kendaraan_obj, stasiun_nama in kendaraan_list.items:
        kendaraan_dict = kendaraan_obj.to_dict()
        kendaraan_dict['stasiun_nama'] = stasiun_nama
        results.append(kendaraan_dict)
    
    return jsonify({
        'kendaraan': results,
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
    
    # FIXED: Changed default status to 'Tersedia' to match model
    kendaraan = Kendaraan(
        merk=data.get('merk'),
        tipe=data.get('tipe'),
        status=data.get('status', 'Tersedia'),
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

# FIXED: Changed from maintenance to laporan routes
@kendaraan_bp.route('/<int:kendaraan_id>/laporan', methods=['GET'])
@jwt_required()
def get_laporan_logs(kendaraan_id):
    # Check if kendaraan exists
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = LogLaporan.query.filter_by(kendaraan_id=kendaraan_id)
    
    if status:
        query = query.filter(LogLaporan.status == status)
    
    logs = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'laporan_logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    }), 200

# routes/kendaraan.py

@kendaraan_bp.route('/<int:kendaraan_id>/laporan', methods=['POST'])
@jwt_required()
def create_laporan_log(kendaraan_id):
    # 1. Mendapatkan data user
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # 2. Mendapatkan data kendaraan
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    
    # 3. Mendapatkan data dari request body
    data = request.get_json()
    if not data.get('laporan'):
        return jsonify({'message': 'Laporan field is required'}), 400
    
    # 4. Membuat objek LogLaporan baru
    log = LogLaporan(
        kendaraan_id=kendaraan_id,
        nrp=current_user_nrp,
        laporan=data.get('laporan'),
        status=data.get('status', 'Dilaporkan')
    )
    
    # 5. Menyimpan ke database
    db.session.add(log)
    db.session.commit() # <-- KEMUNGKINAN BESAR CRASH TERJADI DI SINI
    
    return jsonify({
        'message': 'Laporan created successfully',
        'log': log.to_dict()
    }), 201

@kendaraan_bp.route('/laporan/<int:log_laporan_id>', methods=['PUT'])
@jwt_required()
def update_laporan_log(log_laporan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    log = LogLaporan.query.get_or_404(log_laporan_id)
    
    # Only admin or the reporter can update
    if user.role != 'admin' and log.nrp != current_user_nrp:
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Users can only update laporan, admins can update everything
    if user.role == 'admin':
        log.laporan = data.get('laporan', log.laporan)
        log.status = data.get('status', log.status)
        log.tanggal_pemeliharaan = data.get('tanggal_pemeliharaan', log.tanggal_pemeliharaan)
    else:
        # Regular users can only update their own laporan if status is still 'Dilaporkan'
        if log.status == 'Dilaporkan':
            log.laporan = data.get('laporan', log.laporan)
        else:
            return jsonify({'message': 'Cannot update laporan that is already processed'}), 403
    
    db.session.commit()
    
    return jsonify({
        'message': 'Laporan updated successfully',
        'log': log.to_dict()
    }), 200

@kendaraan_bp.route('/laporan/<int:log_laporan_id>', methods=['DELETE'])
@jwt_required()
def delete_laporan_log(log_laporan_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    log = LogLaporan.query.get_or_404(log_laporan_id)
    
    # Only admin or the reporter can delete (and only if status is 'Dilaporkan')
    if user.role != 'admin' and (log.nrp != current_user_nrp or log.status != 'Dilaporkan'):
        return jsonify({'message': 'Access denied'}), 403
    
    db.session.delete(log)
    db.session.commit()
    
    return jsonify({'message': 'Laporan deleted successfully'}), 200

# Get all laporan logs (for admin)
@kendaraan_bp.route('/laporan', methods=['GET'])
@jwt_required()
def get_all_laporan_logs():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    kendaraan_id = request.args.get('kendaraan_id', type=int)
    
    query = LogLaporan.query
    
    if status:
        query = query.filter(LogLaporan.status == status)
    if kendaraan_id:
        query = query.filter(LogLaporan.kendaraan_id == kendaraan_id)
    
    logs = query.order_by(LogLaporan.tanggal_laporan.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'laporan_logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    }), 200