from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User
from flask import jsonify


def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()

            try:
                current_user_id = int(current_user_id)
            except (TypeError, ValueError):
                return jsonify({"msg": "Invalid token identity"}), 401

            user = User.query.get(current_user_id)

            if not user:
                return jsonify({"msg": "User not found"}), 404
            if not user.is_active:
                return jsonify({"msg": "Your account has been deactivated."}), 403
            if user.role != role:
                return jsonify({"msg": "Access denied. Insufficient permissions."}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
