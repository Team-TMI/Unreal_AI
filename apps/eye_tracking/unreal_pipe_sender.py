import win32pipe, win32file, pywintypes
import struct
import threading
from utils.packet_utils import pack_eye_tracking_response
from gaze_modular import run_gaze_estimation

PIPE_NAME = r'\\.\pipe\unreal_pipe'
NOTIFY_STRUCT_FORMAT = '<BBBB'  # QuizID, SettingStart, Start, End

import win32pipe, win32file, pywintypes
import struct
import threading

PIPE_NAME = r'\\.\pipe\unreal_pipe'
NOTIFY_STRUCT_FORMAT = '<BBBB'  # QuizID, SettingStart, Start, End

def start_pipe_server(stop_event=None, pipe_ready_event=None):
    print(f"📡 [Pipe] Named Pipe 서버 모드 시작 대기 중: {PIPE_NAME}")
    pipe = win32pipe.CreateNamedPipe(
        PIPE_NAME,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
        2, 65536, 65536, 0, None
    )
    print("🕒 [Pipe] Named Pipe 생성 완료, ConnectNamedPipe() 호출 준비 (메인 스레드)")

    try:
        win32pipe.ConnectNamedPipe(pipe, None)
        print("🔗 [Pipe] ConnectNamedPipe 연결 완료")

        if pipe_ready_event:
            pipe_ready_event.set()

        print("🎯 [Pipe] 클라이언트 연결 대기 중")

    except Exception as e:
        print(f"❌ [Pipe] 연결 실패: {e}")

    return pipe  # ✅ 여기에 return 추가


def handle_client(pipe, stop_event):
    print("👂 [Pipe] 클라이언트 통신 루프 진입")
    # 바로 run_gaze_estimation 호출
    run_gaze_estimation(pipe=pipe, stop_event=stop_event)
