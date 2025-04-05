from flask import Flask, render_template, request, jsonify
import paramiko

app = Flask(__name__)

@app.route('/')
def index():
    #return render_template('index.html')
    return render_template('index3.html')

@app.route('/connect_ssh', methods=['POST'])
def connect_ssh():
    data = request.json
    serverip = data.get('serverip')
    username = data.get('username')
    password = data.get('password')
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(serverip, username=username, password=password)
        
        stdin, stdout, stderr = client.exec_command('ls')  # 테스트용 명령어 실행
        output = stdout.read().decode()
        client.close()
        
        return jsonify({'status': 'success', 'output': output})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
