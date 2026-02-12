from flask import Blueprint, request, jsonify, send_from_directory
import logging
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from models import db, User

# 配置日志
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        logger.warning('Registration attempt with missing fields')
        return jsonify({'msg': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        logger.warning(f'Registration attempt with existing username: {username}')
        return jsonify({'msg': 'Username already exists'}), 409
    if User.query.filter_by(email=email).first():
        logger.warning(f'Registration attempt with existing email: {email}')
        return jsonify({'msg': 'Email already registered'}), 409

    try:
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        logger.info(f'User registered successfully: {username}')
        return jsonify({'msg': 'User created successfully'}), 201
    except Exception as e:
        logger.error(f'Error during registration: {e}')
        db.session.rollback()
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logger.warning('Login attempt with missing credentials')
        return jsonify({'msg': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        logger.warning(f'Failed login attempt for user: {username}')
        return jsonify({'msg': 'Invalid username or password'}), 401

    try:
        access_token = create_access_token(identity=user.id)
        logger.info(f'User logged in successfully: {username}')
        return jsonify({'access_token': access_token, 'username': user.username}), 200
    except Exception as e:
        logger.error(f'Error during login: {e}')
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            logger.warning(f'Protected route access with invalid user ID: {current_user_id}')
            return jsonify({'msg': 'User not found'}), 404
        logger.info(f'Protected route accessed by user: {user.username}')
        return jsonify({'msg': f'Hello {user.username}'}), 200
    except Exception as e:
        logger.error(f'Error in protected route: {e}')
        return jsonify({'msg': 'Internal server error'}), 500

# 登录页面
@auth_bp.route('/login-page')
def login_page():
    return send_from_directory('templates', 'login.html')

# 注册页面
@auth_bp.route('/register-page')
def register_page():
    return send_from_directory('templates', 'register.html')