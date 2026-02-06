# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app
from app.models import User, Curso, Documento, Horario, Mensaje, CursoProfesor
from app import db

profesor_bp = Blueprint('profesor', __name__, url_prefix='/profesor')

# --- HELPER: VERIFICACIÓN DE SEGURIDAD ---
def obtener_curso_del_profesor(curso_id):
    """
    Verifica si el curso existe y si el profesor actual lo imparte.
    Retorna el objeto Curso o None si no tiene permiso.
    """
    user_id = session.get('user_id')
    # Optimización: Usamos la relación directa definida en models.py
    profesor = User.query.get(user_id)
    
    # Busca el curso dentro de los cursos impartidos por este profesor
    curso = Curso.query.filter_by(id=curso_id).first()
    
    if curso and curso in profesor.cursos_impartidos:
        return curso
    return None

@profesor_bp.before_request
def require_profesor():
    """Middleware de seguridad para todas las rutas del blueprint."""
    if 'user_id' not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for('auth.login'))
    if session.get('role') != 'profesor':
        flash("Acceso restringido a claustro docente.", "error")
        return redirect(url_for('auth.dashboard'))

# =======================================================
#  GESTIÓN DE CATÁLOGO Y CURSOS
# =======================================================

@profesor_bp.route('/catalogo')
def catalogo():
    user_id = session['user_id']
    profesor = User.query.get(user_id)
    
    # Obtener IDs de cursos ya impartidos para la vista
    cursos_impartidos_ids = {c.id for c in profesor.cursos_impartidos}
    todos_cursos = Curso.query.all()
    
    return render_template('profesor/catalogo.html', cursos=todos_cursos, impartidos=cursos_impartidos_ids)

@profesor_bp.route('/asignar/<int:curso_id>')
def asignar_curso(curso_id):
    user_id = session['user_id']
    profesor = User.query.get(user_id)
    curso = Curso.query.get_or_404(curso_id)

    if curso in profesor.cursos_impartidos:
        flash("Ya estás asignado a este curso.", "info")
    else:
        # Uso de la relación SQLAlchemy para añadir (más limpio)
        profesor.cursos_impartidos.append(curso)
        db.session.commit()
        flash(f"Has tomado la cátedra de {curso.nombre}.", "success")
    
    return redirect(url_for('profesor.catalogo'))

@profesor_bp.route('/dejar/<int:curso_id>')
def dejar_curso(curso_id):
    user_id = session['user_id']
    profesor = User.query.get(user_id)
    curso = Curso.query.get_or_404(curso_id)

    if curso in profesor.cursos_impartidos:
        profesor.cursos_impartidos.remove(curso)
        db.session.commit()
        flash("Has dejado la cátedra.", "info")
    else:
        flash("No impartías este curso.", "error")
        
    return redirect(url_for('profesor.catalogo'))

# =======================================================
#  GESTIÓN DE DOCUMENTOS
# =======================================================

@profesor_bp.route('/subir/<int:curso_id>', methods=['GET', 'POST'])
def subir_documento(curso_id):
    curso = obtener_curso_del_profesor(curso_id)
    if not curso:
        flash("Acceso denegado a este curso.", "error")
        return redirect(url_for('profesor.catalogo'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        tipo = request.form.get('tipo')
        archivo = request.files.get('archivo')
        
        if not titulo or not archivo or not archivo.filename:
            flash("Todos los campos son obligatorios.", "error")
        else:
            try:
                filename = secure_filename(archivo.filename)
                # Usar configuración de la app para la ruta (Más robusto)
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                
                archivo.save(os.path.join(upload_path, filename))
                
                nuevo_doc = Documento(
                    titulo=titulo,
                    ruta_archivo=filename,
                    tipo=tipo,
                    profesor_id=session['user_id'],
                    curso_id=curso.id
                )
                db.session.add(nuevo_doc)
                db.session.commit()
                flash("Recurso académico publicado.", "success")
            except Exception as e:
                flash(f"Error al subir archivo: {e}", "error")
                
        return redirect(url_for('profesor.subir_documento', curso_id=curso.id))
    
    return render_template('profesor/subir_documento.html', curso=curso)

# =======================================================
#  GESTIÓN DE HORARIOS (TUTORÍAS)
# =======================================================

@profesor_bp.route('/horario/<int:curso_id>', methods=['GET', 'POST'])
def gestionar_horario(curso_id):
    curso = obtener_curso_del_profesor(curso_id)
    if not curso:
        flash("No impartes este curso.", "error")
        return redirect(url_for('profesor.catalogo'))
    
    if request.method == 'POST':
        try:
            fecha_hora_str = request.form['fecha_hora']
            duracion = int(request.form['duracion'])
            
            # Convertir hora local (España) a UTC
            from datetime import datetime, timezone
            fecha_hora_local = datetime.fromisoformat(fecha_hora_str)
            # España en invierno: UTC+1 → restamos 1 hora para convertir a UTC
            fecha_hora_utc = fecha_hora_local - timedelta(hours=1)
            
            # Limpieza: Un profesor solo un horario activo por curso a la vez (Opcional)
            Horario.query.filter_by(curso_id=curso.id, profesor_id=session['user_id']).delete()
            
            nuevo_horario = Horario(
                fecha_hora=fecha_hora_utc,
                duracion_minutos=duracion,
                tipo='en_vivo',
                profesor_id=session['user_id'],
                curso_id=curso.id
            )
            db.session.add(nuevo_horario)
            db.session.commit()
            flash("Sesión en vivo programada.", "success")
        except ValueError:
            flash("Formato de fecha inválido.", "error")
            
        return redirect(url_for('profesor.gestionar_horario', curso_id=curso.id))
    
    # Mostrar horarios futuros ordenados
    horarios = Horario.query.filter_by(
        curso_id=curso.id, 
        profesor_id=session['user_id']
    ).order_by(Horario.fecha_hora.asc()).all()
    
    return render_template('profesor/horario.html', curso=curso, horarios=horarios)

@profesor_bp.route('/eliminar_horario/<int:horario_id>')
def eliminar_horario(horario_id):
    # Verificamos que el horario pertenezca al profesor logueado
    horario = Horario.query.filter_by(id=horario_id, profesor_id=session['user_id']).first_or_404()
    curso_id = horario.curso_id
    
    db.session.delete(horario)
    db.session.commit()
    flash("Horario cancelado.", "info")
    return redirect(url_for('profesor.gestionar_horario', curso_id=curso_id))

# =======================================================
#  SISTEMA DE MENSAJERÍA Y CHAT
# =======================================================

@profesor_bp.route('/chat')
def chat():
    """Vista general de chats: Muestra los cursos activos del profesor."""
    from app.models import limpiar_mensajes_antiguos
    limpiar_mensajes_antiguos() # Mantenimiento automático
    
    user_id = session['user_id']
    profesor = User.query.get(user_id)
    # Usar la relación directa es más eficiente que filtrar Curso.id.in_([...])
    return render_template('profesor/chat.html', cursos=profesor.cursos_impartidos)

@profesor_bp.route('/chat/<int:curso_id>', methods=['GET', 'POST'])
def chat_curso(curso_id):
    curso = obtener_curso_del_profesor(curso_id)
    if not curso:
        return redirect(url_for('profesor.chat'))
    
    user_id = session['user_id']

    if request.method == 'POST':
        contenido = request.form.get('mensaje', '').strip()
        
        # Lógica mejorada: Responder al último alumno que escribió
        # O idealmente, recibir el destinatario_id desde un hidden input en el form
        destinatario_id = request.form.get('destinatario_id')
        
        if not destinatario_id:
            # Fallback: Buscar el último alumno si no se especifica (Legacy mode)
            ultimo_msg = Mensaje.query.filter(
                Mensaje.curso_id == curso.id,
                Mensaje.destinatario_id == user_id,
                Mensaje.tipo == 'asincrono'  # 👈 FILTRAR POR TIPO
            ).order_by(Mensaje.fecha.desc()).first()
            
            if ultimo_msg:
                destinatario_id = ultimo_msg.remitente_id
        
        if contenido and destinatario_id:
            nuevo_mensaje = Mensaje(
                curso_id=curso.id,
                remitente_id=user_id,
                destinatario_id=destinatario_id,
                contenido=contenido,
                tipo='asincrono'  # 👈 ESPECIFICAR TIPO
            )
            db.session.add(nuevo_mensaje)
            db.session.commit()
            flash("Mensaje enviado.", "success")
        else:
            flash("No se pudo enviar el mensaje. Falta destinatario o contenido.", "error")
            
        return redirect(url_for('profesor.chat_curso', curso_id=curso.id))
    
    # Cargar historial de 72h (solo asíncrono)
    limite = datetime.utcnow() - timedelta(hours=72)
    mensajes = Mensaje.query.filter(
        Mensaje.curso_id == curso.id,
        Mensaje.tipo == 'asincrono',  # 👈 FILTRAR POR TIPO
        Mensaje.fecha >= limite
    ).order_by(Mensaje.fecha.asc()).all()
    
    return render_template('profesor/chat_curso.html', curso=curso, mensajes=mensajes)

@profesor_bp.route('/chat_vivo/<int:curso_id>')
def chat_vivo(curso_id):
    curso = obtener_curso_del_profesor(curso_id)
    if not curso: return redirect(url_for('profesor.catalogo'))
    
    user_id = session['user_id']
    ahora = datetime.utcnow()
    
    # Verificar si hay una sesión activa usando la relación del modelo
    # Esto es más eficiente que hacer una query separada si ya tenemos el objeto curso
    # (Aunque aquí hacemos query para filtrar por fecha)
    horario_activo = Horario.query.filter(
        Horario.curso_id == curso.id,
        Horario.profesor_id == user_id,
        Horario.fecha_hora <= ahora,
        # Nota: SQLite no soporta sumar tiempo directo en query complejo fácilmente, 
        # así que filtramos los recientes y comprobamos en Python o usamos lógica simple
    ).order_by(Horario.fecha_hora.desc()).first()

    # Validación precisa de tiempo en Python
    en_vivo = False
    if horario_activo:
        fin = horario_activo.fecha_hora + timedelta(minutes=horario_activo.duracion_minutos)
        if ahora <= fin:
            en_vivo = True
    
    if not en_vivo:
        flash("No hay sesión en vivo programada para este momento.", "info")
        return redirect(url_for('profesor.gestionar_horario', curso_id=curso.id))
    
    # Cargar solo mensajes síncronos
    mensajes_previos = Mensaje.query.filter(
        Mensaje.curso_id == curso.id,
        Mensaje.tipo == 'sincrono'  # 👈 FILTRAR POR TIPO
    ).order_by(Mensaje.fecha.asc()).all()
    
    return render_template('profesor/chat_vivo.html', curso=curso, mensajes_previos=mensajes_previos)

@profesor_bp.route('/chat_vivo_global')
def chat_vivo_global():
    """Panel de control para ver todas las sesiones activas del profesor."""
    user_id = session['user_id']
    profesor = User.query.get(user_id)
    
    ahora = datetime.utcnow()
    horarios_activos = []
    
    # Iteramos sobre los cursos que el profesor YA imparte (usando la relación)
    for curso in profesor.cursos_impartidos:
        # Buscamos horarios de este curso y profesor
        horarios = Horario.query.filter_by(curso_id=curso.id, profesor_id=user_id).all()
        
        for h in horarios:
            fin = h.fecha_hora + timedelta(minutes=h.duracion_minutos)
            if h.fecha_hora <= ahora <= fin:
                horarios_activos.append({
                    'curso': curso,
                    'horario': h
                })
    
    return render_template('profesor/chat_vivo_global.html', horarios_activos=horarios_activos)