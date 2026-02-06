# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from app.models import Curso, Inscripcion, Documento, Mensaje, User, Horario
from app import db

alumno_bp = Blueprint('alumno', __name__, url_prefix='/alumno')

@alumno_bp.before_request
def require_alumno():
    # ✅ Excluir rutas de autenticación para evitar bucles
    if request.endpoint in ['auth.login', 'auth.register', 'auth.logout']:
        return
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') != 'alumno':
        return "Acceso denegado", 403

@alumno_bp.route('/catalogo')
def catalogo():
    cursos = Curso.query.all()
    user_id = session['user_id']
    inscritos = {i.curso_id for i in Inscripcion.query.filter_by(alumno_id=user_id).all()}
    return render_template('alumno/catalogo.html', cursos=cursos, inscritos=inscritos)

@alumno_bp.route('/curso/<int:curso_id>')
def ver_profesores(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    profesores = curso.profesores
    return render_template('alumno/ver_profesores.html', curso=curso, profesores=profesores)

@alumno_bp.route('/inscribir/<int:curso_id>/<int:profesor_id>')
def inscribir(curso_id, profesor_id):
    user_id = session['user_id']
    
    from app.models import CursoProfesor
    if not CursoProfesor.query.filter_by(curso_id=curso_id, profesor_id=profesor_id).first():
        flash("El profesor no imparte este curso.", "error")
        return redirect(url_for('alumno.catalogo'))
    
    if Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id, profesor_id=profesor_id).first():
        flash("Ya estás inscrito en este curso con este profesor.", "info")
        return redirect(url_for('alumno.catalogo'))
    
    inscripcion = Inscripcion(
        alumno_id=user_id,
        curso_id=curso_id,
        profesor_id=profesor_id
    )
    db.session.add(inscripcion)
    db.session.commit()
    flash("¡Inscripción exitosa!", "success")
    return redirect(url_for('alumno.catalogo'))

@alumno_bp.route('/cancelar/<int:curso_id>')
def cancelar(curso_id):
    user_id = session['user_id']
    inscripciones = Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id).all()
    for insc in inscripciones:
        db.session.delete(insc)
    db.session.commit()
    flash("Inscripción(es) cancelada(s).", "info")
    return redirect(url_for('alumno.catalogo'))

@alumno_bp.route('/mis_cursos')
def mis_cursos():
    user_id = session['user_id']
    inscripciones = Inscripcion.query.filter_by(alumno_id=user_id).all()
    
    ahora = datetime.utcnow()
    for insc in inscripciones:
        horarios = Horario.query.filter(
            Horario.curso_id == insc.curso_id,
            Horario.profesor_id == insc.profesor_id
        ).all()
        insc.tiene_tutoria_activa = False
        for h in horarios:
            fin = h.fecha_hora + timedelta(minutes=h.duracion_minutos)
            if h.fecha_hora <= ahora <= fin:
                insc.tiene_tutoria_activa = True
                break
    
    return render_template('alumno/cursos.html', inscripciones=inscripciones)

@alumno_bp.route('/documentos')
def documentos():
    user_id = session['user_id']
    inscripciones = Inscripcion.query.filter_by(alumno_id=user_id).all()
    documentos = []
    for insc in inscripciones:
        docs = Documento.query.filter_by(curso_id=insc.curso_id, profesor_id=insc.profesor_id).all()
        documentos.extend(docs)
    return render_template('alumno/documentos.html', documentos=documentos)

@alumno_bp.route('/documentos/<int:curso_id>')
def documentos_curso(curso_id):
    user_id = session['user_id']
    inscripcion = Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id).first()
    if not inscripcion:
        return "No tienes acceso a este curso.", 403
    
    documentos = Documento.query.filter_by(
        curso_id=curso_id,
        profesor_id=inscripcion.profesor_id
    ).all()
    curso = Curso.query.get_or_404(curso_id)
    return render_template('alumno/documentos_curso.html', documentos=documentos, curso=curso)

@alumno_bp.route('/chat')
def chat():
    from app.models import limpiar_mensajes_antiguos
    limpiar_mensajes_antiguos()
    
    user_id = session['user_id']
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    inscripciones = Inscripcion.query.filter_by(alumno_id=user_id).all()
    
    if not inscripciones:
        return render_template('alumno/chat_no_inscrito.html')
    
    cursos_info = []
    combinaciones_vistas = set()  # Para evitar duplicados
    
    for insc in inscripciones:
        clave = (insc.curso_id, insc.profesor_id)
        if clave in combinaciones_vistas:
            continue
        combinaciones_vistas.add(clave)
        
        curso = Curso.query.get(insc.curso_id)
        profesor = User.query.get(insc.profesor_id)
        if curso and profesor:
            cursos_info.append({'curso': curso, 'profesor': profesor})
    
    return render_template('alumno/chat.html', cursos_info=cursos_info)

@alumno_bp.route('/chat/<int:curso_id>', methods=['GET', 'POST'])
def chat_curso(curso_id):
    user_id = session['user_id']
    inscripcion = Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id).first()
    if not inscripcion:
        return "No tienes acceso.", 403
    
    curso = Curso.query.get_or_404(curso_id)
    profesor_id = inscripcion.profesor_id
    
    if request.method == 'POST':
        contenido = request.form['mensaje'].strip()
        if not contenido:
            flash("El mensaje no puede estar vacío.", "error")
            return redirect(url_for('alumno.chat_curso', curso_id=curso_id))
        
        nuevo_mensaje = Mensaje(
            curso_id=curso_id,
            remitente_id=user_id,
            destinatario_id=profesor_id,
            contenido=contenido,
            tipo='asincrono'  # 👈 ESPECIFICAR TIPO
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()
        flash("Mensaje enviado al profesor.", "success")
        return redirect(url_for('alumno.chat_curso', curso_id=curso_id))
    
    limite = datetime.utcnow() - timedelta(hours=72)
    mensajes = Mensaje.query.filter(
        Mensaje.curso_id == curso_id,
        Mensaje.tipo == 'asincrono',  # 👈 FILTRAR POR TIPO
        ((Mensaje.remitente_id == user_id) & (Mensaje.destinatario_id == profesor_id)) |
        ((Mensaje.remitente_id == profesor_id) & (Mensaje.destinatario_id == user_id)),
        Mensaje.fecha >= limite
    ).order_by(Mensaje.fecha.asc()).all()
    
    return render_template('alumno/chat_curso.html', curso=curso, mensajes=mensajes)

@alumno_bp.route('/chat_vivo_global')
def chat_vivo_global():
    user_id = session['user_id']
    inscripciones = Inscripcion.query.filter_by(alumno_id=user_id).all()
    
    ahora = datetime.utcnow()
    horarios_activos = []
    combinaciones_vistas = set()  # Para evitar duplicados
    
    for insc in inscripciones:
        curso = Curso.query.get(insc.curso_id)
        profesor = User.query.get(insc.profesor_id)
        if not curso or not profesor:
            continue
        
        # Crear una clave única para evitar duplicados
        clave = (insc.curso_id, insc.profesor_id)
        if clave in combinaciones_vistas:
            continue
        combinaciones_vistas.add(clave)
        
        horarios = Horario.query.filter(
            Horario.curso_id == insc.curso_id,
            Horario.profesor_id == insc.profesor_id
        ).all()
        
        for h in horarios:
            fin = h.fecha_hora + timedelta(minutes=h.duracion_minutos)
            if h.fecha_hora <= ahora <= fin:
                horarios_activos.append({
                    'curso': curso,
                    'profesor': profesor,
                    'horario': h
                })
                break  # Solo necesitamos un horario activo por curso/profesor
    
    return render_template('alumno/chat_vivo_global.html', horarios_activos=horarios_activos)

@alumno_bp.route('/chat_vivo/<int:curso_id>')
def chat_vivo(curso_id):
    user_id = session['user_id']
    inscripcion = Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id).first()
    if not inscripcion:
        flash("No estás inscrito en este curso.", "error")
        return redirect(url_for('alumno.mis_cursos'))
    
    curso = Curso.query.get_or_404(curso_id)
    profesor = User.query.get(inscripcion.profesor_id)
    
    ahora = datetime.utcnow()
    horarios = Horario.query.filter(
        Horario.curso_id == curso_id,
        Horario.profesor_id == profesor.id
    ).all()

    horario_activo = None
    for h in horarios:
        fin = h.fecha_hora + timedelta(minutes=h.duracion_minutos)
        if h.fecha_hora <= ahora <= fin:
            horario_activo = h
            break

    if not horario_activo:
        flash("No hay una tutoría en vivo en este momento.", "info")
        return redirect(url_for('alumno.mis_cursos'))
    
    # Solo mensajes sincronos
    mensajes_previos = Mensaje.query.filter(
        Mensaje.curso_id == curso_id,
        Mensaje.tipo == 'sincrono'  # 👈 FILTRAR POR TIPO
    ).order_by(Mensaje.fecha.asc()).all()
    
    return render_template('alumno/chat_vivo.html', curso=curso, profesor=profesor, mensajes_previos=mensajes_previos)

@alumno_bp.route('/ia/<int:curso_id>')
def ia_ayuda(curso_id):
    user_id = session['user_id']
    inscripcion = Inscripcion.query.filter_by(alumno_id=user_id, curso_id=curso_id).first()
    if not inscripcion:
        flash("No tienes acceso a este curso.", "error")
        return redirect(url_for('alumno.mis_cursos'))
    
    curso = Curso.query.get_or_404(curso_id)
    return render_template('alumno/ia_ayuda.html', curso=curso)

# =======================================================
#  SISTEMA DE IA NEXUS CORE
# =======================================================

@alumno_bp.route('/api/ia', methods=['POST'])
def ia_api():
    """API para la IA Nexus - sin API keys, funciona offline"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '').strip()
        curso_id = data.get('curso_id')
        
        if not pregunta or not curso_id:
            return jsonify({'error': 'Faltan datos'}), 400
        
        # Obtener contexto del curso
        curso = Curso.query.get_or_404(curso_id)
        contexto = obtener_contexto_curso(curso.nombre)
        
        # Generar respuesta contextual
        respuesta = generar_respuesta_contextual(pregunta, contexto, curso.nombre)
        
        return jsonify({'respuesta': respuesta})
        
    except Exception as e:
        return jsonify({'error': 'Error en el sistema de IA'}), 500

def obtener_contexto_curso(nombre_curso):
    contextos = {
        'HTML': "HTML es el lenguaje de marcado estándar para crear páginas web. Se usa para estructurar contenido con etiquetas como <div>, <p>, <h1>, etc. Los elementos HTML se anidan para crear estructuras jerárquicas.",
        'CSS': "CSS es el lenguaje de hojas de estilo que describe la presentación de documentos HTML. Se usa para definir colores, fuentes, márgenes, posicionamiento y diseño responsive. Las reglas CSS tienen selectores y propiedades.",
        'Python': "Python es un lenguaje de programación de alto nivel, interpretado y orientado a objetos. Es conocido por su sintaxis clara y legible. Tiene tipos de datos como listas, diccionarios, tuplas y soporta programación funcional y orientada a objetos.",
        'Matemáticas': "Las matemáticas incluyen álgebra, geometría, cálculo, estadística y más. El álgebra trata con variables y ecuaciones, la geometría con formas y espacios, y el cálculo con tasas de cambio y acumulación.",
        'Inglés': "El inglés tiene gramática basada en sujeto-verbo-objeto, tiempos verbales (presente, pasado, futuro), y vocabulario extenso. Las reglas incluyen uso de artículos (a, an, the), preposiciones y formación de plurales.",
        'Español': "El español es una lengua romance con género gramatical (masculino/femenino), número (singular/plural), y conjugación verbal compleja. Tiene acentos ortográficos y reglas de puntuación específicas.",
        'Historia': "La historia estudia eventos pasados, civilizaciones, guerras, revoluciones y desarrollo cultural. Incluye periodos como la antigüedad, edad media, renacimiento, revolución industrial y mundo contemporáneo.",
        'Literatura': "La literatura incluye géneros como narrativa, poesía, teatro y ensayo. Elementos clave son trama, personajes, ambientación, tema y estilo. Autores importantes varían por época y región.",
        'Biología': "La biología estudia la vida y los organismos vivos. Incluye células, genética, evolución, ecología, anatomía y fisiología. Los seres vivos se clasifican en reinos y comparten características como metabolismo y reproducción.",
        'Economía': "La economía estudia producción, distribución y consumo de bienes y servicios. Conceptos clave incluyen oferta y demanda, mercado, inflación, PIB, y políticas fiscales y monetarias."
    }
    return contextos.get(nombre_curso, "Curso educativo general de GC ACADEMIA.")

def generar_respuesta_contextual(pregunta, contexto, curso_nombre):
    # Lógica mejorada para respuestas relevantes
    pregunta_lower = pregunta.lower()
    
    # Saludos y despedidas
    if any(palabra in pregunta_lower for palabra in ['hola', 'buenas', 'saludos', 'hey', 'hi']):
        return f"¡Saludos! Soy tu asistente IA para {curso_nombre}. Puedo ayudarte con dudas sobre el curso o guiarte en el uso de la plataforma. ¿En qué necesitas ayuda?"
    
    elif any(palabra in pregunta_lower for palabra in ['gracias', 'thank', 'muchas gracias']):
        return "¡De nada! Estoy aquí para ayudarte con tus estudios y el uso de la plataforma."
    
    elif any(palabra in pregunta_lower for palabra in ['adiós', 'chao', 'bye', 'hasta luego']):
        return "¡Hasta luego! No dudes en volver si necesitas ayuda con tus estudios o la plataforma."
    
    # Guía de navegación - Preguntas comunes
    elif any(palabra in pregunta_lower for palabra in ['inscribir', 'inscripción', 'matricular', 'apuntar']):
        return "Para inscribirte a un curso:\n1. Ve a 'Catálogo' en el menú\n2. Elige el curso que te interesa\n3. Selecciona un profesor disponible\n4. Haz clic en 'Inscribirse'\n\n¡Es así de fácil!"
    
    elif any(palabra in pregunta_lower for palabra in ['materiales', 'documentos', 'recursos', 'archivos', 'pdf']):
        return "Puedes acceder a los materiales del curso de dos formas:\n• En 'Mis Cursos' → selecciona tu curso\n• Directamente en 'Materiales' en el menú principal\n\nAllí encontrarás apuntes, ejercicios y recursos subidos por tu profesor."
    
    elif any(palabra in pregunta_lower for palabra in ['chat', 'mensaje', 'profesor', 'comunicar', 'hablar']):
        return "Para chatear con tu profesor:\n1. Ve a 'Chat con Profesor' en el menú\n2. Selecciona el curso correspondiente\n3. Escribe tu mensaje y envíalo\n\nTambién puedes usar el chat durante las tutorías en vivo para preguntas en tiempo real."
    
    elif any(palabra in pregunta_lower for palabra in ['tutoría', 'en vivo', 'sesión', 'clase en vivo', 'chat vivo']):
        return "Para acceder a tutorías en vivo:\n1. Ve a 'Chat en Vivo' en el menú\n2. Espera a que aparezca tu curso cuando el profesor esté disponible\n3. Haz clic en 'Entrar al chat'\n\nLas tutorías tienen horarios programados por tu profesor."
    
    elif any(palabra in pregunta_lower for palabra in ['cursos', 'mis cursos', 'ver cursos']):
        return "En 'Mis Cursos' puedes ver todos los cursos en los que estás inscrito, verificar si hay tutorías activas y acceder rápidamente a materiales y chat."
    
    elif any(palabra in pregunta_lower for palabra in ['catálogo', 'cursos disponibles', 'ver todos']):
        return "El 'Catálogo' muestra todos los cursos disponibles en la plataforma. Puedes ver qué profesores imparten cada curso y si ya estás inscrito en alguno."
    
    elif any(palabra in pregunta_lower for palabra in ['ayuda', 'uso', 'navegar', 'funciona', 'utilizar']):
        return "Guía rápida de la plataforma:\n\n📚 **Catálogo**: Explora cursos disponibles\n🎓 **Mis Cursos**: Gestiona tus inscripciones\n📁 **Materiales**: Accede a recursos del curso\n💬 **Chat con Profesor**: Comunicación asíncrona\n🔴 **Chat en Vivo**: Tutorías en tiempo real\n🤖 **Asistente IA**: Ayuda instantánea (¡como ahora!)"
    
    elif len(pregunta) < 5:
        return "Por favor, formula una pregunta más completa para poder ayudarte mejor."
    
    # Respuestas contextualizadas por curso
    else:
        respuestas_curso = [
            f"Excelente pregunta sobre {curso_nombre}. Te recomiendo revisar los materiales del curso o preguntar a tu profesor en el chat en vivo.",
            f"Para entender mejor '{pregunta[:30]}...', te sugiero practicar con los ejercicios proporcionados en el curso.",
            f"Este concepto es fundamental en {curso_nombre}. ¿Te gustaría que te lo explique de otra manera?",
            f"Te recomiendo consultar la documentación oficial o los recursos que tu profesor ha subido para este tema.",
            f"En {curso_nombre}, este tema es crucial. Te sugiero revisar los conceptos fundamentales antes de avanzar a ejercicios prácticos."
        ]
        return respuestas_curso[len(pregunta) % len(respuestas_curso)]