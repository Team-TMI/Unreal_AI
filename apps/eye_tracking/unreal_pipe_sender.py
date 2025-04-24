import time
import queue
from utils.packet_utils import dict_to_packet


PIPE_NAME = r'\\.\pipe\unreal_pipe'
_q = queue.Queue()


def pipe_sender():
    print(f"📡 Unreal 파이프로 전송 시도 중: {PIPE_NAME}")
    while True:
        try:
            with open(PIPE_NAME, 'wb') as pipe:
                print("✅ Unreal과 파이프 연결됨")
                while True:
                    data = _q.get()
                    if isinstance(data, dict):
                        packed = dict_to_packet(data)
                        pipe.write(packed)
                        pipe.flush()
                        print(f"🚀 패킷 전송 완료 (quiz_id={data['quiz_id']}, x={data['x']}, y={data['y']})")
        except Exception as e:
            print(f"❌ 파이프 연결 실패, 재시도 중... ({e})")
            time.sleep(2)

def get_queue():
    return _q

# 🔁 다른 큐에서 받아서 이 모듈의 q로 옮기는 함수
def forward_to_unreal(src_q, dest_q):
    while True:
        try:
            data = src_q.get(timeout=0.1)
            dest_q.put(data)
        except queue.Empty:
            continue
