from multiprocessing import Process, Event
from gaze_modular import run_gaze_estimation
from unreal_pipe_sender import start_pipe_server

if __name__ == "__main__":
    USE_GAZE_ESTIMATION = True
    SHOW_FACE_MESH_IN_TRACKER = True
    USE_PIPE_SERVER = True

    stop_event = Event()
    processes = []

    if USE_GAZE_ESTIMATION:
        processes.append(Process(target=run_gaze_estimation, args=(None, SHOW_FACE_MESH_IN_TRACKER, stop_event)))

    if USE_PIPE_SERVER:
        processes.append(Process(target=start_pipe_server, args=(stop_event,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("✅ 모든 프로세스 정상 종료")
