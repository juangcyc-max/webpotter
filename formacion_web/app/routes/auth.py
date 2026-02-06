# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.models import User
from app import db

# Nota: Ya no necesitamos importar generate_password_hash aquí 
# porque lo manejamos dentro del modelo User (más limpio).

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Redirige al dashboard si hay sesión, o al login si no."""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capturamos datos del formulario
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # 1. Validación básica
        if not all([username, email, password, role]):
            flash('Por favor completa todos los campos.')
            return render_template('register.html') # Recarga con el error

        if role not in ['alumno', 'profesor', 'admin']:
            flash('Rol seleccionado no válido.')
            return render_template('register.html')

        # 2. Verificar si ya existe en la Base de Datos
        if User.query.filter_by(username=username).first():
            flash('Ese nombre de usuario ya está ocupado.')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Ese correo electrónico ya está registrado.')
            return redirect(url_for('auth.register'))

        # 3. Crear nuevo usuario (Usando el método seguro del modelo)
        try:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password) # ¡Encriptación automática!
            
            db.session.add(new_user)
            db.session.commit()

            # 4. Éxito: Redirigir al login
            flash('Cuenta creada con éxito. Por favor inicia sesión.')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error en el sistema estelar. Inténtalo de nuevo.')
            print(f"Error DB: {e}")

    # Si es GET, mostramos el formulario
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Buscar usuario
        user = User.query.filter_by(username=username).first()

        # Verificar contraseña con el método seguro del modelo
        if user and user.check_password(password):
            # Crear sesión
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            
            # Redirigir al dashboard
            return redirect(url_for('auth.dashboard'))
        else:
            # Fallo: Mostrar alerta holográfica roja
            flash('Credenciales inválidas. Acceso denegado.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/dashboard')
def dashboard():
    """Centro de control: Redirige según el rol del usuario."""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al Nexus.')
        return redirect(url_for('auth.login'))
    
    role = session.get('role')
    
    if role == 'alumno':
        return redirect(url_for('alumno.catalogo'))
    elif role == 'profesor':
        return redirect(url_for('profesor.catalogo'))
    elif role == 'admin':
        return redirect(url_for('admin.panel'))
    else:
        # Por seguridad, si el rol es raro, cerramos sesión
        session.clear()
        flash('Error de identidad. Contacta al soporte.')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Desconexión exitosa. Hasta pronto.')
    return redirect(url_for('auth.login'))