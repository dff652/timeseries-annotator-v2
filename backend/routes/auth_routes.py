from flask import Blueprint, jsonify, request
from auth import login_required, verify_password, generate_token, load_users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        if verify_password(username, password):
            token = generate_token(username)
            users = load_users()
            user_info = users.get(username, {})
            
            return jsonify({
                'success': True,
                'token': token,
                'username': username,
                'name': user_info.get('name', username)
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/user', methods=['GET'])
@login_required
def get_current_user(current_user):
    """Get current logged in user info"""
    try:
        users = load_users()
        user_info = users.get(current_user, {})
        return jsonify({
            'success': True,
            'username': current_user,
            'name': user_info.get('name', current_user)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
