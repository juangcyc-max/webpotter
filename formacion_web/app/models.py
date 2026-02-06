# -*- coding: utf-8 -*-
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# --- TABLA DE ASOCIACIÓN (Muchos a Muchos: Profesor <-> Curso) ---
class CursoProfesor(db.Model):
    __tablename__ = 'curso_profesor'
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), primary_key=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

# --- USUARIOS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'alumno', 'profesor', 'admin'
    
    # Relaciones
    inscripciones = db.relationship('Inscripcion', foreign_keys='Inscripcion.alumno_id', backref='alumno', lazy=True, cascade="all, delete-orphan")
    mensajes_enviados = db.relationship('Mensaje', foreign_keys='Mensaje.remitente_id', backref='remitente', lazy=True)
    mensajes_recibidos = db.relationship('Mensaje', foreign_keys='Mensaje.destinatario_id', backref='destinatario', lazy=True)

    # Relación muchos a muchos con cursos (Solo para profesores)
    cursos_impartidos = db.relationship(
        'Curso',
        secondary='curso_profesor',
        backref=db.backref('profesores', lazy='dynamic')
    )

    # --- SEGURIDAD DE CONTRASEÑAS (CRÍTICO) ---
    def set_password(self, password):
        """Encripta la contraseña antes de guardarla."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña introducida coincide con el hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

# --- CURSOS ---
class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    
    # Relaciones
    documentos = db.relationship('Documento', backref='curso_rel', lazy=True, cascade="all, delete-orphan")
    horarios = db.relationship('Horario', backref='curso_rel', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Curso {self.nombre}>'

# --- INSCRIPCIONES ---
class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    
    curso = db.relationship('Curso', backref='inscripciones_curso', lazy=True)
    profesor = db.relationship('User', foreign_keys=[profesor_id], backref='inscripciones_como_profesor')

# --- DOCUMENTOS ---
class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20)) # pdf, video, etc.
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    profesor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    
    curso = db.relationship('Curso', viewonly=True) # viewonly para evitar conflictos con backref de arriba

# --- HORARIOS (Clases en vivo) ---
class Horario(db.Model):
    __tablename__ = 'horarios'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    duracion_minutos = db.Column(db.Integer, default=60)
    tipo = db.Column(db.String(20), default='en_vivo')
    
    profesor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)

# --- MENSAJERÍA ---
class Mensaje(db.Model):
    __tablename__ = 'mensajes'
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    remitente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(10), default='asincrono')  # 👈 CAMBIO CLAVE

# --- PAGOS ---
class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(50))

# --- SOPORTE TÉCNICO ---
class Soporte(db.Model):
    __tablename__ = 'soporte'
    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    respuesta = db.Column(db.Text)
    fecha_respuesta = db.Column(db.DateTime)
    resuelto = db.Column(db.Boolean, default=False)  # 👈 CAMPO AÑADIDO


# =========================================
#   FUNCIÓN DE LIMPIEZA DE MENSAJES ANTIGUOS
# =========================================
def limpiar_mensajes_antiguos():
    """
    Elimina mensajes asíncronos con más de 72 horas de antigüedad.
    Mantiene los mensajes de chat en vivo (tipo diferente).
    """
    try:
        limite = datetime.utcnow() - timedelta(hours=72)
        
        # Eliminar solo mensajes asíncronos antiguos
        mensajes_antiguos = Mensaje.query.filter(
            Mensaje.tipo == 'asincrono',
            Mensaje.fecha < limite
        ).all()
        
        count = len(mensajes_antiguos)
        
        for mensaje in mensajes_antiguos:
            db.session.delete(mensaje)
        
        db.session.commit()
        
        if count > 0:
            print(f"🧹 Limpieza automática: {count} mensajes antiguos eliminados.")
        
        return count
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en limpieza de mensajes: {e}")
        return 0