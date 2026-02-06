from flask_socketio import join_room, leave_room, send
from app import socketio, db
from flask import session
from app.models import Mensaje

# Almacenar conexiones activas: {sala: set(user_ids)}
conexiones_activas = {}

def get_sala(curso_id, profesor_id):
    return f"curso_{curso_id}_profesor_{profesor_id}"

@socketio.on('join')
def on_join(data):
    curso_id = data['curso_id']
    profesor_id = data['profesor_id']
    user_id = session.get('user_id')
    sala = get_sala(curso_id, profesor_id)
    
    join_room(sala)
    
    # Registrar conexión
    if sala not in conexiones_activas:
        conexiones_activas[sala] = set()
    conexiones_activas[sala].add(user_id)
    
    # Notificar a todos en la sala
    num_alumnos = len([u for u in conexiones_activas[sala] if u != profesor_id])
    send({
        'type': 'conexion_update',
        'alumnos_conectados': num_alumnos
    }, to=sala)
    
    print(f"✅ Usuario {user_id} unido a sala: {sala} | Alumnos: {num_alumnos}")

@socketio.on('leave')
def on_leave(data):
    curso_id = data['curso_id']
    profesor_id = data['profesor_id']
    user_id = session.get('user_id')
    sala = get_sala(curso_id, profesor_id)
    
    leave_room(sala)
    
    # Eliminar conexión
    if sala in conexiones_activas and user_id in conexiones_activas[sala]:
        conexiones_activas[sala].remove(user_id)
    
    # Notificar actualización
    num_alumnos = len([u for u in conexiones_activas[sala] if u != profesor_id]) if sala in conexiones_activas else 0
    send({
        'type': 'conexion_update',
        'alumnos_conectados': num_alumnos
    }, to=sala)
    
    print(f"🚪 Usuario {user_id} salió de sala: {sala} | Alumnos: {num_alumnos}")

@socketio.on('message')
def handle_message(data):
    curso_id = data.get('curso_id')
    profesor_id = data.get('profesor_id')
    mensaje_texto = data.get('mensaje', '').strip()
    user_id = session.get('user_id')
    
    if not mensaje_texto or not user_id:
        return
    
    sala = get_sala(curso_id, profesor_id)
    
    # Guardar en base de datos como mensaje SÍNCRONO
    nuevo_mensaje = Mensaje(
        curso_id=curso_id,
        remitente_id=user_id,
        destinatario_id=profesor_id,
        contenido=mensaje_texto,
        tipo='sincrono'  # 👈 ESPECIFICAR TIPO
    )
    db.session.add(nuevo_mensaje)
    db.session.commit()
    
    # Emitir mensaje
    send({
        'type': 'message',
        'user_id': user_id,
        'mensaje': mensaje_texto
    }, to=sala)