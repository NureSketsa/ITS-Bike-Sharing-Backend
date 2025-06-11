from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.stasiun import Stasiun
from app.models.kendaraan import Kendaraan
from app.models.user import User

stasiun_bp = Blueprint('stasiun', __name__)

@stasiun_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_stasiun():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Stasiun.query
    
    if status:
        query = query.filter(Stasiun.status == status)
    
    stasiun_list = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'stasiun': [s.to_dict() for s in stasiun_list.items],
        'total': stasiun_list.total,
        'pages': stasiun_list.pages,
        'current_page': page
    }), 200

@stasiun_bp.route('/<int:stasiun_id>', methods=['GET'])
@jwt_required()
def get_stasiun(stasiun_id):
    stasiun = Stasiun.query.get_or_404(stasiun_id)
    
    # FIXED: Changed status to match model default 'Tersedia'
    available_bikes = Kendaraan.query.filter_by(
        stasiun_id=stasiun_id, 
        status='Tersedia'
    ).count()
    
    stasiun_data = stasiun.to_dict()
    stasiun_data['available_bikes'] = available_bikes
    
    return jsonify({'stasiun': stasiun_data}), 200

@stasiun_bp.route('/', methods=['POST'])
@jwt_required()
def create_stasiun():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('nama_stasiun'):
        return jsonify({'message': 'nama_stasiun is required'}), 400
    
    # FIXED: Changed default status to match model default 'Aktif'
    stasiun = Stasiun(
        nama_stasiun=data.get('nama_stasiun'),
        alamat=data.get('alamat'),
        status=data.get('status', 'Aktif'),
        latitude=data.get('latitude'),
        longtitude=data.get('longtitude')
    )
    
    db.session.add(stasiun)
    db.session.commit()
    
    return jsonify({
        'message': 'Stasiun created successfully',
        'stasiun': stasiun.to_dict()
    }), 201

@stasiun_bp.route('/<int:stasiun_id>', methods=['PUT'])
@jwt_required()
def update_stasiun(stasiun_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    stasiun = Stasiun.query.get_or_404(stasiun_id)
    data = request.get_json()
    
    stasiun.nama_stasiun = data.get('nama_stasiun', stasiun.nama_stasiun)
    stasiun.alamat = data.get('alamat', stasiun.alamat)
    stasiun.status = data.get('status', stasiun.status)
    # ADDED: Update latitude and longtitude
    stasiun.latitude = data.get('latitude', stasiun.latitude)
    stasiun.longtitude = data.get('longtitude', stasiun.longtitude)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stasiun updated successfully',
        'stasiun': stasiun.to_dict()
    }), 200

@stasiun_bp.route('/<int:stasiun_id>', methods=['DELETE'])
@jwt_required()
def delete_stasiun(stasiun_id):
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    stasiun = Stasiun.query.get_or_404(stasiun_id)
    
    # Check if there are bikes at this station
    bikes_count = Kendaraan.query.filter_by(stasiun_id=stasiun_id).count()
    if bikes_count > 0:
        return jsonify({
            'message': 'Cannot delete station with bikes. Please relocate bikes first.'
        }), 400
    
    db.session.delete(stasiun)
    db.session.commit()
    
    return jsonify({'message': 'Stasiun deleted successfully'}), 200

@stasiun_bp.route('/<int:stasiun_id>/kendaraan', methods=['GET'])
@jwt_required()
def get_stasiun_kendaraan(stasiun_id):
    stasiun = Stasiun.query.get_or_404(stasiun_id)
    
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Kendaraan.query.filter_by(stasiun_id=stasiun_id)
    
    if status:
        query = query.filter(Kendaraan.status == status)
    
    # ADDED: Pagination for better performance
    kendaraan_list = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'stasiun': stasiun.to_dict(),
        'kendaraan': [k.to_dict() for k in kendaraan_list.items],
        'total': kendaraan_list.total,
        'pages': kendaraan_list.pages,
        'current_page': page
    }), 200

@stasiun_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_stasiun_summary():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    # FIXED: Changed status filter to match model default 'Aktif'
    stasiun_list = Stasiun.query.filter_by(status='Aktif').all()
    summary = []
    
    for stasiun in stasiun_list:
        # FIXED: Changed status to match model default 'Tersedia'
        available_bikes = Kendaraan.query.filter_by(
            stasiun_id=stasiun.stasiun_id, 
            status='Tersedia'
        ).count()
        
        total_bikes = Kendaraan.query.filter_by(
            stasiun_id=stasiun.stasiun_id
        ).count()
        
        summary.append({
            'stasiun': stasiun.to_dict(),
            'available_bikes': available_bikes,
            'total_bikes': total_bikes,
            'utilization_rate': round((total_bikes - available_bikes) / total_bikes * 100, 2) if total_bikes > 0 else 0
        })
    
    return jsonify({'summary': summary}), 200

# ADDED: New route to get nearby stations based on coordinates
@stasiun_bp.route('/nearby', methods=['GET'])
@jwt_required()
def get_nearby_stasiun():
    lat = request.args.get('latitude', type=float)
    lng = request.args.get('longitude', type=float)
    radius = request.args.get('radius', 5, type=int)  # km radius
    
    if not lat or not lng:
        return jsonify({'message': 'latitude and longitude parameters are required'}), 400
    
    # For now, return all active stations since we don't have distance calculation
    # In production, you would implement proper distance calculation
    stasiun_list = Stasiun.query.filter_by(status='Aktif').all()
    
    nearby_stations = []
    for stasiun in stasiun_list:
        if stasiun.latitude and stasiun.longtitude:
            # Simple distance check (in real app, use proper geospatial queries)
            available_bikes = Kendaraan.query.filter_by(
                stasiun_id=stasiun.stasiun_id, 
                status='Tersedia'
            ).count()
            
            station_data = stasiun.to_dict()
            station_data['available_bikes'] = available_bikes
            nearby_stations.append(station_data)
    
    return jsonify({
        'nearby_stations': nearby_stations,
        'search_params': {
            'latitude': lat,
            'longitude': lng,
            'radius_km': radius
        }
    }), 200

# ADDED: Route to get station statistics
@stasiun_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_stasiun_statistics():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    total_stations = Stasiun.query.count()
    active_stations = Stasiun.query.filter_by(status='Aktif').count()
    inactive_stations = total_stations - active_stations
    
    total_bikes = Kendaraan.query.count()
    available_bikes = Kendaraan.query.filter_by(status='Tersedia').count()
    
    return jsonify({
        'stations': {
            'total': total_stations,
            'active': active_stations,
            'inactive': inactive_stations
        },
        'bikes': {
            'total': total_bikes,
            'available': available_bikes,
            'in_use': total_bikes - available_bikes
        },
        'overall_utilization_rate': round((total_bikes - available_bikes) / total_bikes * 100, 2) if total_bikes > 0 else 0
    }), 200