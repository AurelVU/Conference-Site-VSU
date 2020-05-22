from datetime import datetime

import models
from init import db
from flask import session
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from init import socketio
from models import User


@socketio.on('joined', namespace='/send_message')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': 'Собеседник вошел в чат'}, room=room)


@socketio.on('text', namespace='/send_message')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    message_bd = models.Message(id_from=int(message['id_from']), id_to=int(message['id_to']), text=message['msg'])
    db.session.add(message_bd)
    db.session.commit()
    emit('message', {'msg': message['msg'], 'recipient_id': message['id_from'], 'timestamp': str(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))}, room=room)


@socketio.on('left', namespace='/send_message')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': 'Собеседник покинул чат'}, room=room)

