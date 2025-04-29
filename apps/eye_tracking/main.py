from multiprocessing import Event
from unreal_pipe_sender import start_pipe_server
from gaze_modular import run_gaze_estimation

if __name__ == "__main__":
    stop_event = Event()
    pipe_ready_event = Event()

    pipe = start_pipe_server(stop_event=stop_event, pipe_ready_event=pipe_ready_event)

    # 서버 파이프가 열리고 클라이언트 연결까지 완료될 때까지 대기
    pipe_ready_event.wait()

    if pipe is not None:
        print("🚀 파이프 준비 완료, Gaze Estimation 시작")
        run_gaze_estimation(pipe=pipe, stop_event=stop_event)
    else:
        print("❌ 파이프 생성 실패")
