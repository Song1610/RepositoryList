from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from ssh2 import SSHConnection

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ssh_conn = SSHConnection()  # SSH 세션을 유지하는 객체 생성

@app.route('/')
def index():
    return render_template('index7.html')

@socketio.on('connect_ssh')
def connect_ssh(data):
    serverip = data.get('serverip')
    username = data.get('username')
    password = data.get('password')

    success, message = ssh_conn.connect(serverip, username, password)
    if success:
        emit('ssh_output', {'message': 'SSH 연결 성공'})
    else:
        emit('ssh_output', {'message': f'Error: {message}'})

@socketio.on('execute_command')
def execute_command(data):
    command = data.get('command')
    if command:
        output = ssh_conn.execute_command(command)
        print(f"SSH OUTPUT : {output}")
        emit('ssh_output', {'message': output})

@socketio.on('disconnect_ssh')
def disconnect_ssh():
    ssh_conn.close()
    emit('ssh_output', {'message': 'SSH 세션이 종료되었습니다.'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
