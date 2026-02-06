# -*- coding: utf-8 -*-
from app import create_app, db, socketio  # ← añadido socketio

# Importar modelos para que SQLAlchemy los conozca
from app.models import User, Curso, Inscripcion, Documento, Horario

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas exitosamente en la base de datos.")
    
    # Usar socketio.run() para habilitar WebSockets
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)