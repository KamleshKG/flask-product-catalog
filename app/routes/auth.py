from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user
from app.models.user import User
from app.utils.governance import audit_log

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.verify_password(data['password']):
        # Generate new session token
        token = user.generate_session_token()
        db.session.commit()

        # Log the login
        audit_log(
            user_id=user.id,
            action='login',
            details={'ip': request.remote_addr}
        )

        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.name
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        audit_log(
            user_id=current_user.id,
            action='logout',
            details={'ip': request.remote_addr}
        )
        current_user.generate_session_token()  # Invalidate old token
        db.session.commit()
        logout_user()
    return jsonify({"message": "Logged out"})


@auth_bp.route('/session', methods=['GET'])
@login_required
def check_session():
    return jsonify({
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.name,
            "permissions": [p for p in current_app.config['PERMISSIONS']
                            if current_user.can(p)]
        }
    })