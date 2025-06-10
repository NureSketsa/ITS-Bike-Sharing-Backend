# app/routes/transaksi.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.transaksi import Transaksi
from app.models.kendaraan import Kendaraan
from app.models.stasiun import Stasiun
from datetime import datetime
import uuid

# Nama blueprint tetap sama
transaksi_bp = Blueprint('transaksi', __name__)

# Pola baru dengan satu URL '/rental'
@transaksi_bp.route('/rental', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def manage_rental():
    current_user_nrp = get_jwt_identity()

    # Cari sewa yang sedang aktif milik pengguna ini
    active_rental = Transaksi.query.filter_by(
        user_nrp=current_user_nrp,
        status_transaksi='active'
    ).first()

    # --- LOGIKA UNTUK METODE GET ---
    # Tujuan: Cek status sewa saat ini
    if request.method == 'GET':
        if not active_rental:
            return jsonify({'message': 'No active rental found', 'rental': None}), 200
        return jsonify({'message': 'Active rental found', 'rental': active_rental.to_dict()}), 200

    # --- LOGIKA UNTUK METODE POST ---
    # Tujuan: Memulai sewa baru
    if request.method == 'POST':
        if active_rental:
            return jsonify({'message': 'You already have an active rental'}), 400

        data = request.get_json()
        kendaraan_id = data.get('kendaraan_id')
        stasiun_ambil_id = data.get('stasiun_ambil_id')

        if not kendaraan_id or not stasiun_ambil_id:
            return jsonify({"message": "kendaraan_id and stasiun_ambil_id are required"}), 400

        kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
        if kendaraan.status != 'available':
            return jsonify({'message': 'Bike is not available'}), 400
        if kendaraan.stasiun_id != stasiun_ambil_id:
            return jsonify({'message': 'Bike is not at the specified station'}), 400

        new_transaksi = Transaksi(
            user_nrp=current_user_nrp,
            kendaraan_id=kendaraan_id,
            stasiun_ambil_id=stasiun_ambil_id,
            reference_number=str(uuid.uuid4())[:8].upper(),
            status_transaksi='active'
        )
        kendaraan.status = 'rented'
        kendaraan.stasiun_id = None
        
        db.session.add(new_transaksi)
        db.session.commit()
        return jsonify({'message': 'Bike rented successfully', 'transaksi': new_transaksi.to_dict()}), 201

    # --- LOGIKA UNTUK METODE DELETE ---
    # Tujuan: Mengakhiri sewa
    if request.method == 'DELETE':
        if not active_rental:
            return jsonify({'message': 'No active rental to return'}), 404
            
        data = request.get_json()
        stasiun_kembali_id = data.get('stasiun_kembali_id')
        if not stasiun_kembali_id:
            return jsonify({"message": "stasiun_kembali_id is required"}), 400

        stasiun = Stasiun.query.get_or_404(stasiun_kembali_id)
        kendaraan = Kendaraan.query.get(active_rental.kendaraan_id)

        active_rental.stasiun_kembali_id = stasiun_kembali_id
        active_rental.waktu_kembali = datetime.utcnow()
        active_rental.status_transaksi = 'completed'

        kendaraan.status = 'available'
        kendaraan.stasiun_id = stasiun_kembali_id

        db.session.commit()
        return jsonify({'message': 'Bike returned successfully', 'transaksi': active_rental.to_dict()}), 200