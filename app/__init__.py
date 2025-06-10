from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.kendaraan import kendaraan_bp
    from app.routes.stasiun import stasiun_bp
    from app.routes.transaksi import transaksi_bp
    from app.routes.layanan import layanan_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(kendaraan_bp, url_prefix='/api/kendaraan')
    app.register_blueprint(stasiun_bp, url_prefix='/api/stasiun')
    app.register_blueprint(transaksi_bp, url_prefix='/api/transaksi')
    app.register_blueprint(layanan_bp, url_prefix='/api/layanan')

    # # --- TAMBAHKAN BLOK KODE INI ---
    # print("\n=== DAFTAR SEMUA RUTE YANG TERDAFTAR ===")
    # for rule in app.url_map.iter_rules():
    #     print(f"Endpoint: {rule.endpoint}, Methods: {list(rule.methods)}, URL: {rule.rule}")
    # print("=======================================\n")
    # --------------------------------

    
    return app