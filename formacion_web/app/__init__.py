# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app)

    # Registrar blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.alumno.views import alumno_bp
    app.register_blueprint(alumno_bp)

    from app.routes.admin.views import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.profesor.views import profesor_bp
    app.register_blueprint(profesor_bp)

    from app.routes.soporte import soporte_bp
    app.register_blueprint(soporte_bp)

    # ✅ Registrar eventos de Socket.IO
    from app import events

    return app