import paramiko
import threading
import time
from flask_socketio import SocketIO

class SSHConnection:
    def __init__(self):
        self.client = None
        self.shell = None
        self.is_connected = False

    def connect(self, serverip, username, password):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(serverip, username=username, password=password, timeout=10)

            self.shell = self.client.invoke_shell()
            self.is_connected = True

            # SSH 출력을 실시간으로 수신하는 스레드 실행
            threading.Thread(target=self.listen_to_ssh, daemon=True).start()
            
            return True, "SSH 연결 성공!"
        except Exception as e:
            self.is_connected = False
            return False, str(e)

    def listen_to_ssh(self):
        """SSH에서 발생하는 출력을 지속적으로 확인하여 클라이언트에 전달"""
        while self.is_connected:
            try:
                if self.shell.recv_ready():
                    output = self.shell.recv(1024).decode()

                    # flask-socketio 이용 클라이언트에 출력 전송
                    Socketio.emit('ssh_output', {'message': output})

                    print(f"SSH OUTPUT: {output}")  # 출력 확인용 (Flask에서 emit할 예정)
            except Exception as e:
                print(f"SSH Error: {str(e)}")
                self.is_connected = False
                break
            time.sleep(0.1)

    def execute_command(self, command):
        """SSH 세션을 통해 명령어 실행"""
        if self.shell and self.is_connected:
            self.shell.send(command + "\n")
            time.sleep(0.5)  # 응답을 기다리기 위해 잠시 대기
            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(1024).decode()
            return output
        return "No active SSH session."

    def close(self):
        """SSH 세션 종료"""
        self.is_connected = False
        if self.client:
            self.client.close()
            self.client = None
            self.shell = None
