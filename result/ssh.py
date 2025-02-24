import paramiko
import threading

clients = {}  # 클라이언트별 SSH 세션 저장

def connect_ssh(data, session_id, socketio):
    serverip = data.get('serverip')
    username = data.get('username')
    password = data.get('password')

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(serverip, username=username, password=password)

        shell = client.invoke_shell()
        clients[session_id] = shell  # 클라이언트별 SSH 세션 저장

        socketio.emit('ssh_output', {'status': 'success', 'message': 'Connected to server'}, room=session_id)

        def listen_to_shell():
            while True:
                try:
                    output = shell.recv(1024).decode()
                    if output:
                        socketio.emit('ssh_output', {'status': 'success', 'message': output}, room=session_id)
                except Exception:
                    break

        thread = threading.Thread(target=listen_to_shell, daemon=True)
        thread.start()

    except Exception as e:
        socketio.emit('ssh_output', {'status': 'error', 'message': str(e)}, room=session_id)

def execute_command(session_id, command, socketio):
    shell = clients.get(session_id)
    if shell:
        shell.send(command + '\n')
    else:
        socketio.emit('ssh_output', {'status': 'error', 'message': 'No active SSH session'}, room=session_id)

def disconnect_ssh(session_id):
    shell = clients.pop(session_id, None)
    if shell:
        shell.close()
