# -*- coding: utf-8 -*-
import csv
from io import StringIO
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, Response
from app.models import Curso, User, Inscripcion, Pago, Horario, Mensaje, CursoProfesor
from app import db as db_instance

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') != 'admin':
        return "Acceso denegado", 403

@admin_bp.route('/inicializar_cursos')
def inicializar_cursos():
    cursos_nombres = [
        "HTML", "CSS", "Python", "Inglés", "Español",
        "Matemáticas", "Historia", "Literatura", "Biología", "Economía"
    ]
    
    creados = 0
    for nombre in cursos_nombres:
        if not Curso.query.filter_by(nombre=nombre).first():
            curso = Curso(nombre=nombre)
            db_instance.session.add(curso)
            creados += 1
    
    db_instance.session.commit()
    mensaje = f"✅ {creados} cursos nuevos creados." if creados else "ℹ️ Todos los cursos ya existían."
    flash(mensaje, "success")
    return redirect(url_for('admin.panel'))

@admin_bp.route('/panel')
def panel():
    # === TODOS LOS ALUMNOS (incluso sin inscripciones) ===
    todos_alumnos = User.query.filter_by(role='alumno').all()
    alumnos_con_inscripciones = []
    alumnos_sin_inscripciones = []
    
    for alumno in todos_alumnos:
        inscs = Inscripcion.query.filter_by(alumno_id=alumno.id).all()
        if inscs:
            for insc in inscs:
                curso = Curso.query.get(insc.curso_id)
                profesor = User.query.get(insc.profesor_id)
                pago = Pago.query.filter_by(alumno_id=alumno.id, curso_id=insc.curso_id).first()
                alumnos_con_inscripciones.append({
                    'alumno': alumno,
                    'curso': curso,
                    'profesor': profesor,
                    'pago_realizado': pago is not None,
                    'inscripcion_id': insc.id
                })
        else:
            alumnos_sin_inscripciones.append({
                'alumno': alumno,
                'curso': None,
                'profesor': None,
                'pago_realizado': False,
                'inscripcion_id': None
            })
    
    # Combinar ambos grupos (los con inscripciones primero)
    inscripciones_alumnos = alumnos_con_inscripciones + alumnos_sin_inscripciones

    # === TODOS LOS PROFESORES (incluso sin cursos) ===
    todos_profesores = User.query.filter_by(role='profesor').all()
    profesores_actividad = []
    
    for prof in todos_profesores:
        cursos_impartidos = CursoProfesor.query.filter_by(profesor_id=prof.id).count()
        horarios = Horario.query.filter_by(profesor_id=prof.id).count()
        mensajes = Mensaje.query.filter_by(remitente_id=prof.id).count()
        total_actividad = cursos_impartidos + horarios + mensajes
        
        profesores_actividad.append({
            'profesor': prof,
            'cursos_impartidos': cursos_impartidos,
            'horarios': horarios,
            'mensajes': mensajes,
            'total_actividad': total_actividad
        })
    
    return render_template(
        'admin/panel.html',
        inscripciones_alumnos=inscripciones_alumnos,
        profesores_actividad=profesores_actividad
    )

@admin_bp.route('/eliminar_inscripcion/<int:inscripcion_id>')
def eliminar_inscripcion(inscripcion_id):
    insc = Inscripcion.query.get_or_404(inscripcion_id)
    db_instance.session.delete(insc)
    db_instance.session.commit()
    flash("Inscripción eliminada correctamente.", "success")
    return redirect(url_for('admin.panel'))

@admin_bp.route('/eliminar_profesor/<int:profesor_id>')
def eliminar_profesor(profesor_id):
    # Eliminar dependencias
    Inscripcion.query.filter_by(profesor_id=profesor_id).delete()
    Horario.query.filter_by(profesor_id=profesor_id).delete()
    CursoProfesor.query.filter_by(profesor_id=profesor_id).delete()
    Mensaje.query.filter_by(remitente_id=profesor_id).delete()
    
    # Eliminar al profesor
    profesor = User.query.get_or_404(profesor_id)
    db_instance.session.delete(profesor)
    db_instance.session.commit()
    
    flash(f"Profesor '{profesor.username}' y toda su actividad eliminados.", "success")
    return redirect(url_for('admin.panel'))

# ✅ NUEVA RUTA: Eliminar alumno completamente
@admin_bp.route('/eliminar_alumno/<int:alumno_id>')
def eliminar_alumno(alumno_id):
    # Eliminar dependencias del alumno
    Inscripcion.query.filter_by(alumno_id=alumno_id).delete()
    Pago.query.filter_by(alumno_id=alumno_id).delete()
    from app.models import Soporte
    Soporte.query.filter_by(remitente_id=alumno_id).delete()
    Mensaje.query.filter_by(remitente_id=alumno_id).delete()
    Mensaje.query.filter_by(destinatario_id=alumno_id).delete()
    
    # Eliminar al alumno
    alumno = User.query.get_or_404(alumno_id)
    db_instance.session.delete(alumno)
    db_instance.session.commit()
    
    flash(f"Alumno '{alumno.username}' y toda su actividad eliminados.", "success")
    return redirect(url_for('admin.panel'))

@admin_bp.route('/registrar_pago', methods=['GET', 'POST'])
def registrar_pago():
    if request.method == 'POST':
        alumno_id = request.form['alumno_id']
        curso_id = request.form['curso_id']
        monto = float(request.form['monto'])
        metodo = request.form['metodo']
        
        # Verificar que no exista ya un pago
        pago_existente = Pago.query.filter_by(
            alumno_id=alumno_id,
            curso_id=curso_id
        ).first()
        
        if pago_existente:
            flash("Este alumno ya ha pagado por este curso.", "info")
        else:
            nuevo_pago = Pago(
                alumno_id=alumno_id,
                curso_id=curso_id,
                monto=monto,
                metodo=metodo
            )
            db_instance.session.add(nuevo_pago)
            db_instance.session.commit()
            flash("Pago registrado correctamente.", "success")
        
        return redirect(url_for('admin.panel'))
    
    # Obtener listas para el formulario
    alumnos = User.query.filter_by(role='alumno').all()
    cursos = Curso.query.all()
    return render_template('admin/registrar_pago.html', alumnos=alumnos, cursos=cursos)

# === EXPORTACIONES ===
@admin_bp.route('/exportar/alumnos')
def exportar_alumnos():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Alumno', 'Curso', 'Profesor', 'Estado Pago', 'Fecha Inscripción'])
    
    # Exportar todos los alumnos, incluso sin inscripciones
    todos_alumnos = User.query.filter_by(role='alumno').all()
    for alumno in todos_alumnos:
        inscripciones = Inscripcion.query.filter_by(alumno_id=alumno.id).all()
        if inscripciones:
            for insc in inscripciones:
                curso = Curso.query.get(insc.curso_id)
                profesor = User.query.get(insc.profesor_id)
                pago = Pago.query.filter_by(alumno_id=insc.alumno_id, curso_id=insc.curso_id).first()
                estado_pago = "Pagado" if pago else "No pagado"
                fecha_insc = insc.fecha_inscripcion.strftime('%d/%m/%Y') if insc.fecha_inscripcion else ''
                
                writer.writerow([
                    alumno.username,
                    curso.nombre if curso else '',
                    profesor.username if profesor else '',
                    estado_pago,
                    fecha_insc
                ])
        else:
            # Alumno sin inscripciones
            writer.writerow([
                alumno.username,
                'Sin inscripción',
                'N/A',
                'N/A',
                'N/A'
            ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=alumnos_completos.csv"}
    )

@admin_bp.route('/exportar/profesores')
def exportar_profesores():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Profesor', 'Cursos Impartidos', 'Horarios', 'Mensajes', 'Total Actividad'])
    
    profesores = User.query.filter_by(role='profesor').all()
    for prof in profesores:
        cursos_impartidos = CursoProfesor.query.filter_by(profesor_id=prof.id).count()
        horarios = Horario.query.filter_by(profesor_id=prof.id).count()
        mensajes = Mensaje.query.filter_by(remitente_id=prof.id).count()
        total_actividad = cursos_impartidos + horarios + mensajes
        
        writer.writerow([
            prof.username,
            cursos_impartidos,
            horarios,
            mensajes,
            total_actividad
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=actividad_profesores.csv"}
    )