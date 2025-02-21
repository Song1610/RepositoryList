from flask import Flask, render_template, request, jsonify
import paramiko
import threading
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index4.html')

@socketio.on('connect_ssh')
def connect_ssh(data):
    serverip = data.get('serverip')
    username = data.get('username')
    password = data.get('password')
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(serverip, username=username, password=password)
        
        shell = client.invoke_shell()
        emit('ssh_output', {'status': 'success', 'message': 'Connected to server'})
        
        def listen_to_shell():
            while True:
                output = shell.recv(1024).decode()
                if output:
                    socketio.emit('ssh_output', {'status': 'success', 'message': output})
        
        thread = threading.Thread(target=listen_to_shell)
        thread.start()
        
    except Exception as e:
        emit('ssh_output', {'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)
