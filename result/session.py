import threading
import time
import ssh

# 세션 타이머 저장
session_timers = {}

# 세션 타이머 초기화 및 갱신 함수
def reset_session_timer(session_id, socketio):
    """ 세션 타이머를 초기화하거나 갱신하여 10분 후 자동 종료되도록 설정 """
    if session_id in session_timers:
        session_timers[session_id]['active'] = False  # 기존 타이머 비활성화

    def session_timeout():
        """ 일정 시간(10분) 후 세션 종료 """
        time.sleep(600)  # 10분 (600초) 대기
        if session_timers.get(session_id, {}).get('active'):
            ssh.disconnect_ssh(session_id)  # SSH 세션 종료
            socketio.emit('ssh_output', {'status': 'error', 'message': '세션이 시간 초과로 종료되었습니다.'}, room=session_id)
            del session_timers[session_id]  # 세션 타이머 삭제

    # 새로운 타이머 시작
    session_timers[session_id] = {'active': True}
    threading.Thread(target=session_timeout, daemon=True).start()

