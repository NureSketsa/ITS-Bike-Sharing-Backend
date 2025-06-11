# transaksi.py (FIXED AND CLEANED)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.transaksi import Transaksi
from app.models.kendaraan import Kendaraan
from app.models.stasiun import Stasiun
from app.models.user import User
from app.models.layanan import Layanan, TransaksiLayanan
from datetime import datetime
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

transaksi_bp = Blueprint('transaksi', __name__)

# Helper function for consistent error handling
def handle_error(e, message="An error occurred"):
    logger.error(f"Error in transaksi blueprint: {str(e)}")
    db.session.rollback()
    return jsonify({'error': message, 'details': str(e)}), 500

# Helper function to get current user safely
def get_current_user():
    try:
        current_user_nrp = get_jwt_identity()
        user = User.query.filter_by(nrp=current_user_nrp).first()
        if not user:
            return None, jsonify({'error': 'User not found'}), 404
        return user, None, None
    except Exception as e:
        return None, jsonify({'error': 'Invalid token', 'details': str(e)}), 401

@transaksi_bp.route('/rent', methods=['POST'])
@jwt_required()
def rent_bike():
    """Rent a bike"""
    try:
        user, error_response, status_code = get_current_user()
        if error_response:
            return error_response, status_code
        
        # NOTE: Logic to block multiple rentals was removed as per user request.
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        kendaraan_id = data.get('kendaraan_id')
        stasiun_ambil_id = data.get('stasiun_ambil_id')
        
        if not kendaraan_id or not stasiun_ambil_id:
            return jsonify({'error': 'kendaraan_id and stasiun_ambil_id are required'}), 400
        
        kendaraan = Kendaraan.query.get(kendaraan_id)
        if not kendaraan:
            return jsonify({'error': 'Vehicle not found'}), 404
        # NOTE: Status check is case-insensitive by converting both to upper.
        if kendaraan.status.upper() != 'TERSEDIA':
            return jsonify({'error': f'Vehicle is not available. Status: {kendaraan.status}'}), 400
        
        stasiun = Stasiun.query.get(stasiun_ambil_id)
        if not stasiun:
            return jsonify({'error': 'Station not found'}), 404
        
        transaksi = Transaksi(
            user_nrp=user.nrp,
            kendaraan_id=kendaraan_id,
            stasiun_ambil_id=stasiun_ambil_id,
            waktu_mulai=datetime.utcnow(),
            status_transaksi='ONGOING',
            payment_gateway_ref=str(uuid.uuid4())
        )
        
        db.session.add(transaksi)
        kendaraan.status = 'DISEWA'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bike rented successfully',
            'data': transaksi.to_dict()
        }), 201
        
    except Exception as e:
        return handle_error(e, "Failed to process rental request")

@transaksi_bp.route('/return', methods=['POST'])
@jwt_required()
def return_bike():
    """Return a bike"""
    try:
        user, error_response, status_code = get_current_user()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        stasiun_kembali_id = data.get('stasiun_kembali_id')
        transaksi_id = data.get('transaksi_id')
        
        if not stasiun_kembali_id or not transaksi_id:
            return jsonify({'error': 'transaksi_id and stasiun_kembali_id are required'}), 400
        
        stasiun = Stasiun.query.get(stasiun_kembali_id)
        if not stasiun:
            return jsonify({'error': 'Return station not found'}), 404
        
        transaksi = Transaksi.query.filter_by(
            transaksi_id=transaksi_id,
            user_nrp=user.nrp,
            status_transaksi='ONGOING'
        ).first()
        
        if not transaksi:
            return jsonify({'error': 'Active rental with this ID not found for the current user'}), 404
        
        waktu_selesai = datetime.utcnow()
        duration = waktu_selesai - transaksi.waktu_mulai
        duration_hours = duration.total_seconds() / 3600
        
        basic_cost = max(5000, duration_hours * 5000)
        
        transaksi.stasiun_kembali_id = stasiun_kembali_id
        transaksi.waktu_selesai = waktu_selesai
        transaksi.status_transaksi = 'SELESAI'
        transaksi.total_biaya = basic_cost
        
        if transaksi.kendaraan:
            transaksi.kendaraan.status = 'TERSEDIA'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bike returned successfully',
            'data': transaksi.to_dict()
        })
        
    except Exception as e:
        return handle_error(e, "Failed to process return request")

@transaksi_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_rentals():
    """Get all of current user's active rentals"""
    try:
        user, error_response, status_code = get_current_user()
        if error_response:
            return error_response, status_code
        
        active_rentals_list = Transaksi.query.filter_by(
            user_nrp=user.nrp,
            status_transaksi='ONGOING'
        ).order_by(Transaksi.waktu_mulai.desc()).all()
        
        if not active_rentals_list:
            return jsonify({
                'success': True,
                'message': 'No active rentals found',
                'data': []
            })
        
        results = []
        for rental in active_rentals_list:
            rental_data = rental.to_dict()
            if rental.waktu_mulai:
                duration = datetime.utcnow() - rental.waktu_mulai
                rental_data['current_duration_hours'] = round(duration.total_seconds() / 3600, 2)
            results.append(rental_data)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return handle_error(e, "Failed to get active rentals")

@transaksi_bp.route('/my-rentals', methods=['GET'])
@jwt_required()
def get_my_rentals():
    """Get current user's rental history"""
    try:
        user, error_response, status_code = get_current_user()
        if error_response:
            return error_response, status_code
            
        query = Transaksi.query.filter_by(user_nrp=user.nrp).order_by(Transaksi.waktu_mulai.desc())
        
        rentals = query.all()
        
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in rentals]
        })
        
    except Exception as e:
        return handle_error(e, "Failed to get rental history")

# This route is optional, you can add it back if needed for admins
@transaksi_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_transactions_for_admin():
    """(Admin) Get all transactions from all users"""
    try:
        user, error_response, status_code = get_current_user()
        if error_response:
            return error_response, status_code

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        all_transactions = Transaksi.query.order_by(Transaksi.waktu_mulai.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in all_transactions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': all_transactions.total,
                'pages': all_transactions.pages
            }
        })
    except Exception as e:
        return handle_error(e, "Failed to get all transactions")