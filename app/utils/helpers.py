from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def admin_required(f):
    """Decorator to require admin role for accessing endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_nrp = get_jwt_identity()
        user = User.query.filter_by(nrp=current_user_nrp).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def user_owns_resource(resource_user_nrp):
    """Check if current user owns the resource"""
    current_user_nrp = get_jwt_identity()
    user = User.query.filter_by(nrp=current_user_nrp).first()
    
    return user.role == 'admin' or current_user_nrp == resource_user_nrp

def generate_response(message, data=None, status_code=200):
    """Generate standardized API response"""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in request data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        return {
            'error': True,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    return {'error': False}

def paginate_query(query, page=1, per_page=20):
    """Helper function to paginate database queries"""
    paginated = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return {
        'items': paginated.items,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }