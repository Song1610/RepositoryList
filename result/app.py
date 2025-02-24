from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import ssh  # ssh.py를 불러오기

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index2.html')

@socketio.on('connect_ssh')
def handle_connect_ssh(data):
    session_id = request.sid  # 클라이언트 세션 ID
    ssh.connect_ssh(data, session_id, socketio)

@socketio.on('execute_command')
def handle_execute_command(data):
    session_id = request.sid
    command = data.get('command')
    ssh.execute_command(session_id, command, socketio)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    ssh.disconnect_ssh(session_id)

# 600초 뒤 세션끊기추가
import session  # session.py 불러오기

@socketio.on('connect_ssh')
def handle_connect_ssh(data):
    session_id = request.sid
    ssh.connect_ssh(data, session_id, socketio)
    session.reset_session_timer(session_id, socketio)  # ⬅ 세션 타이머 시작

@socketio.on('execute_command')
def handle_execute_command(data):
    session_id = request.sid
    command = data.get('command')
    ssh.execute_command(session_id, command, socketio)
    session.reset_session_timer(session_id, socketio)  # ⬅ 명령어 입력 시 타이머 리셋

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    ssh.disconnect_ssh(session_id)


if __name__ == '__main__':
    socketio.run(app, debug=True)
