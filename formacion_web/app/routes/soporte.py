# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from app.models import Soporte, User
from app import db as db_instance
from datetime import datetime

soporte_bp = Blueprint('soporte', __name__, url_prefix='/soporte')

@soporte_bp.route('/', methods=['GET', 'POST'])
def index():
    user_id = session['user_id']
    
    if request.method == 'POST':
        mensaje = request.form['mensaje'].strip()
        if not mensaje:
            flash("El mensaje no puede estar vacío.", "error")
        else:
            nuevo = Soporte(
                remitente_id=user_id,
                mensaje=mensaje
            )
            db_instance.session.add(nuevo)
            db_instance.session.commit()
            flash("Mensaje enviado al administrador. Te responderemos pronto.", "success")
        return redirect(url_for('soporte.index'))
    
    # Cargar historial del usuario
    mensajes = Soporte.query.filter_by(remitente_id=user_id).order_by(Soporte.fecha.desc()).all()
    
    return render_template('soporte/index.html', mensajes=mensajes)

@soporte_bp.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        return "Acceso denegado", 403
    
    todos_mensajes = Soporte.query.order_by(Soporte.fecha.desc()).all()
    
    mensajes_alumnos = []
    mensajes_profesores = []
    
    for msg in todos_mensajes:
        remitente = User.query.get(msg.remitente_id)
        if remitente:
            msg_data = {
                'id': msg.id,
                'remitente_username': remitente.username,
                'remitente_role': remitente.role,
                'mensaje': msg.mensaje,
                'fecha': msg.fecha,
                'leido': msg.leido,
                'respuesta': msg.respuesta,
                'fecha_respuesta': msg.fecha_respuesta,
                'resuelto': msg.resuelto
            }
            if remitente.role == 'alumno':
                mensajes_alumnos.append(msg_data)
            else:
                mensajes_profesores.append(msg_data)
        else:
            # Usuario eliminado - asignar a una categoría genérica
            msg_data = {
                'id': msg.id,
                'remitente_username': 'Usuario eliminado',
                'remitente_role': 'desconocido',
                'mensaje': msg.mensaje,
                'fecha': msg.fecha,
                'leido': msg.leido,
                'respuesta': msg.respuesta,
                'fecha_respuesta': msg.fecha_respuesta,
                'resuelto': msg.resuelto
            }
            mensajes_alumnos.append(msg_data)  # o podrías crear una tercera categoría
    
    return render_template('soporte/admin.html', 
                         mensajes_alumnos=mensajes_alumnos, 
                         mensajes_profesores=mensajes_profesores)
    
   

@soporte_bp.route('/responder/<int:id>', methods=['POST'])
def responder(id):
    if session.get('role') != 'admin':
        return "Acceso denegado", 403
    
    msg = Soporte.query.get_or_404(id)
    respuesta = request.form['respuesta'].strip()
    if respuesta:
        msg.respuesta = respuesta
        msg.fecha_respuesta = datetime.utcnow()
        msg.leido = True
        db_instance.session.commit()
        flash("Respuesta enviada.", "success")
    
    return redirect(url_for('soporte.admin_panel'))

# ✅ FUNCIÓN AÑADIDA: Marcar como resuelto
@soporte_bp.route('/resolver/<int:id>', methods=['POST'])
def resolver_mensaje(id):
    if session.get('role') != 'admin':
        return "Acceso denegado", 403
    
    msg = Soporte.query.get_or_404(id)
    msg.resuelto = True
    db_instance.session.commit()
    flash("Expediente marcado como resuelto.", "success")
    return redirect(url_for('soporte.admin_panel'))

# ✅ FUNCIÓN AÑADIDA: Eliminar mensaje
@soporte_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_mensaje(id):
    if session.get('role') != 'admin':
        return "Acceso denegado", 403
    
    msg = Soporte.query.get_or_404(id)
    db_instance.session.delete(msg)
    db_instance.session.commit()
    flash("Expediente archivado permanentemente.", "success")
    return redirect(url_for('soporte.admin_panel'))

# ✅ FUNCIÓN AÑADIDA: Eliminar mensaje propio (para alumnos y profesores)
@soporte_bp.route('/eliminar_propio/<int:id>', methods=['POST'])
def eliminar_mensaje_propio(id):
    if session.get('role') not in ['alumno', 'profesor']:
        return "Acceso denegado", 403
    
    user_id = session['user_id']
    msg = Soporte.query.filter_by(id=id, remitente_id=user_id).first_or_404()
    
    db_instance.session.delete(msg)
    db_instance.session.commit()
    flash("Mensaje eliminado correctamente.", "success")
    return redirect(url_for('soporte.index'))