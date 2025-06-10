from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(nrp=data.get('nrp')).first():
        return jsonify({'message': 'NRP already exists'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        nrp=data.get('nrp'),
        nama=data.get('nama'),
        email=data.get('email'),
        no_hp=data.get('no_hp'),
        role=data.get('role', 'user')
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nrp = data.get('nrp')
    password = data.get('password')
    
    user = User.query.filter_by(nrp=nrp).first()
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=nrp)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    if user:
        return jsonify({'user': user.to_dict()}), 200
    
    return jsonify({'message': 'User not found'}), 404