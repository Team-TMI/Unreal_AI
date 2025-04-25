import time
import queue
import struct
from utils.packet_utils import pack_eye_tracking_request, pack_eye_tracking_response, pack_eye_tracking_notify


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
                        if data.get("type") == "calibration":
                            packed = pack_eye_tracking_request(
                                quiz_id = data["quiz_id"],
                                width = data["width"],
                                height = data["height"],
                                start = data["start"],
                                end = data["end"]
                            )
                        elif data.get("type") == "notify":
                            packed = pack_eye_tracking_notify(
                                quiz_id = data["quiz_id"],
                                settingStart = data["settingstart"],
                                start = data["start"],
                                end = data["end"]
                            )
                        else:
                            packed = pack_eye_tracking_response(
                                quiz_id = data["quiz_id"],
                                x = data["x"],
                                y = data["y"],
                                blink = data["blink"],
                                state = data["state"]
                            )
                        pipe.write(packed)
                        pipe.flush()
                        print(f"🚀 패킷 전송 완료")
        except Exception as e:
            print(f"❌ 파이프 연결 실패, 재시도 중... ({e})")
            time.sleep(2)

def get_queue():
    return _q


# 다른 큐에서 받아서 Unreal을 통해 보내는 forward 함수
def forward_to_unreal(src_q, dest_q):
    while True:
        try:
            data = src_q.get(timeout=0.1)
            dest_q.put(data)
        except queue.Empty:
            continue


# Unreal에서 보내는 Notify 파트 수신 함수
NOTIFY_STRUCT_FORMAT = '<BBBB'  # QuizID, SettingStart, Start, End

def start_pipe_receiver(on_notify_callback):
    print(f"🔼 Unreal 파이프 리시버 시작: {PIPE_NAME}")
    while True:
        try:
            with open(PIPE_NAME, 'rb') as pipe:
                print("✅ Unreal 파이프와 연결됨 (수신 대기 중)")
                while True:
                    data = pipe.read(4)  # NotifyMessage = 4 bytes
                    if not data:
                        continue

                    if len(data) != 4:
                        print(f"⚠️ 수신 패키스 길이 이상함: {len(data)} bytes")
                        continue

                    quiz_id, setting_start, start, end = struct.unpack(NOTIFY_STRUCT_FORMAT, data)

                    print(f"🌌 수신된 Notify => QuizID: {quiz_id}, SettingStart: {setting_start}, Start: {start}, End: {end}")

                    if on_notify_callback:
                        on_notify_callback({
                            'quiz_id': quiz_id,
                            'setting_start': setting_start,
                            'start': start,
                            'end': end
                        })

        except Exception as e:
            print(f"❌ 파이프 연결 실패 또는 수신 오류: {e}, 재시도 중...")
            time.sleep(2)