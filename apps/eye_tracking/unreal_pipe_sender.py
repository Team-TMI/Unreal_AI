import win32pipe, win32file
import struct
from gaze_modular import run_calibration, run_tracking
from utils.constants import MessageType, NotifyMessage

PIPE_NAME = r'\\.\pipe\unreal_pipe'

state = {
    "calibrating": False,
    "tracking": False
}

def start_pipe_server(stop_event=None, pipe_ready_event=None):
    print(f"📡 [Pipe] Named Pipe 서버 시작: {PIPE_NAME}")
    pipe = win32pipe.CreateNamedPipe(
        PIPE_NAME,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
        1, 65536, 65536, 0, None
    )

    try:
        win32pipe.ConnectNamedPipe(pipe, None)
        print("🔗 [Pipe] 클라이언트 연결 완료")
        if pipe_ready_event:
            pipe_ready_event.set()
        handle_client(pipe, stop_event)

    except Exception as e:
        print(f"❌ [Pipe] 연결 실패: {e}")


def handle_client(pipe, stop_event):
    print("👂 [Pipe] 클라이언트 통신 시작")
    buffer = b""

    calibration_points = None  # ⭐ 캘리브레이션 결과 저장 변수 추가

    while not stop_event.is_set():
        try:
            result, data = win32file.ReadFile(pipe, 1024)
            buffer += data

            while len(buffer) >= 4:  # 최소 NotifyMessage 크기
                header = struct.unpack('<BBBB', buffer[:4])
                quiz_id, setting_start, start, end = header

                if setting_start not in (0, 1) or start not in (0, 1) or end not in (0, 1):
                    print(f"⚠️ 잘못된 데이터 무시: {header}")
                    buffer = buffer[4:]
                    continue  # 무시하고 다음 데이터로 넘어감
                
                print(f"📩 수신 - QuizID:{quiz_id} SettingStart:{setting_start} Start:{start} End:{end}")

                # 버퍼 정리
                buffer = buffer[4:]

                # 신호 해석 및 상태 전환
                if setting_start == 1:
                    print("🛠️ 칼리브레이션 시작")
                    state["calibrating"] = True
                    state["tracking"] = False
                    calibration_points = run_calibration(pipe)  # ⭐ 결과 저장

                elif start == 1:
                    print("🚀 미션 시작 (좌표 전송)")
                    state["calibrating"] = False
                    state["tracking"] = True
                    run_tracking(pipe, stop_event, calibration_points)  # ⭐ 결과 넘겨줌

                elif end == 1:
                    print("🛑 미션 종료 (좌표 전송 멈춤)")
                    state["tracking"] = False

        except Exception as e:
            print(f"❗ 통신 오류: {e}")
            break

    print("📴 파이프 통신 종료")
    win32file.CloseHandle(pipe)