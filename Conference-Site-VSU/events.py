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
    """
    Событие при входе
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': 'Собеседник вошел в чат'}, room=room)


@socketio.on('text', namespace='/send_message')
def text(message):
    """
    Событие при приеме сообщения
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    room = session.get('room')
    if not (message['msg'].strip() == ""):
        block = models.BlockUser.query.filter_by(id_user=current_user.id).first()
        if (block is None) or not(block.block_message):
            message_bd = models.Message(id_from=int(message['id_from']), id_to=int(message['id_to']), text=message['msg'])
            db.session.add(message_bd)
            db.session.commit()
            emit('message', {'msg': message['msg'], 'recipient_id': message['id_from'], 'timestamp': str(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))}, room=room)


@socketio.on('left', namespace='/send_message')
def left(message):
    """
    Событие при покидании чата
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': 'Собеседник покинул чат'}, room=room)

