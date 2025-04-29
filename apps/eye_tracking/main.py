# main.py
from multiprocessing import Event
from unreal_pipe_sender import start_pipe_server

if __name__ == "__main__":
    stop_event = Event()
    pipe_ready_event = Event()

    start_pipe_server(stop_event=stop_event, pipe_ready_event=pipe_ready_event)
