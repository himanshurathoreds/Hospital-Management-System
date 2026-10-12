# python -m celery -A app.celery beat --loglevel=info
# python -m celery -A app.celery worker --loglevel=info --pool=solo

import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, unset_jwt_cookies, jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from models.models import db, User
from dotenv import load_dotenv

from routes.admin import admin_api
from routes.doctor import doctor_api
from routes.patient import patient_api
from routes.tasks import register_tasks, make_celery, cache

app = Flask(__name__)
load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Default to local SQLite + local Redis for dev; override with env vars in production.
# Render/Heroku-style Postgres URLs start with postgres://, SQLAlchemy needs postgresql://
_db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR,'instance','app.db')}")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

_redis_url = os.environ.get("REDIS_URL")
_cache_type = os.environ.get("CACHE_TYPE", "RedisCache" if _redis_url else "SimpleCache")

app.config.update({
    "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret"),
    "SQLALCHEMY_DATABASE_URI": _db_url,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", "jwt-secret"),
    "JWT_TOKEN_LOCATION": ["headers"],
    "JWT_COOKIE_SECURE": False,
    "JWT_COOKIE_CSRF_PROTECT": True,
    "JWT_HEADER_NAME" : "Authorization",
    "JWT_HEADER_TYPE" : "Bearer",

    "broker_url": _redis_url or "redis://localhost:6379/0",
    'result_backend': _redis_url or "redis://localhost:6379/0",
    "CACHE_TYPE": _cache_type,
    "CACHE_REDIS_URL": _redis_url or "redis://localhost:6379/1",
    "CACHE_DEFAULT_TIMEOUT": 300,
})
print("DB PATH:", app.config["SQLALCHEMY_DATABASE_URI"])
app.register_blueprint(admin_api)
app.register_blueprint(doctor_api)
app.register_blueprint(patient_api)
db.init_app(app)

celery = make_celery(app)
tasks = register_tasks(celery, app)
jwt = JWTManager(app)
app.tasks = tasks
cache.init_app(app)
_cors_origins = os.environ.get("CORS_ORIGINS", "*")
CORS(app, supports_credentials=True, origins=[o.strip() for o in _cors_origins.split(",")])


def init_db():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()

        if admin:
            if admin.role != 'admin':
                admin.role = 'admin'
                admin.is_active = True
                db.session.commit()
                print(f"Admin role corrected for user '{admin.username}'")
        else:
            admin = User(
                username='admin',
                email='admin@hospital.com',
                full_name='Hospital Administrator',
                role='admin',
                contact='1234567890'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")


@app.route('/', methods=['GET'])
@jwt_required()
def index():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "admin":
        return jsonify({"message": "Redirect to admin dashboard"}), 200
    elif user.role == "doctor":
        return jsonify({"message": "Redirect to doctor dashboard"}), 200
    elif user.role == "patient":
        return jsonify({"message": "Redirect to patient dashboard"}), 200
    else:
        return jsonify({"message": "Role not recognized"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if not user.is_active:
            return jsonify({"message": "Your account has been deactivated. Please contact admin."}), 403

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        return jsonify({
            "message": f"Welcome, {user.full_name}!",
            "user": user.full_name,
            "access_token": token,
            "role": user.role
        }), 200
    
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    contact = data.get('contact')
    age = data.get('age')
    gender = data.get('gender')
    address = data.get('address')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    patient = User(
        username=username,
        email=email,
        full_name=full_name,
        contact=contact,
        age=int(age) if age else None,
        gender=gender,
        address=address,
        role="patient"
    )
    patient.set_password(password)

    db.session.add(patient)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

init_db()  # runs on import too, so it also runs under gunicorn in production

@app.route('/tasks/run-daily-reminders', methods=['POST'])
def run_daily_reminders():
    secret = os.environ.get("CRON_SECRET")
    if not secret or request.headers.get("X-Cron-Secret") != secret:
        return jsonify({"message": "Unauthorized"}), 401
    count = tasks["send_daily_reminders"]()
    return jsonify({"message": "Daily reminders sent", "count": count}), 200

@app.route('/tasks/run-monthly-reports', methods=['POST'])
def run_monthly_reports():
    secret = os.environ.get("CRON_SECRET")
    if not secret or request.headers.get("X-Cron-Secret") != secret:
        return jsonify({"message": "Unauthorized"}), 401
    count = tasks["send_monthly_reports"]()
    return jsonify({"message": "Monthly reports sent", "count": count}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)), debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")