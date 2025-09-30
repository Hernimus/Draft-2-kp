from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-sangat-sulit-ditebak'

# Izinkan akses dari React (localhost:3000)
CORS(app)

# Daftarkan blueprint
from .public.routes import public_bp
from .admin.routes import admin_bp

app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
