import struct
import time
from unreal_pipe_sender import start_pipe_server

HEADER_SIZE = 8
DUMMY_HEADER = b'\x00' * HEADER_SIZE

def pack_eye_tracking_response(quiz_id, x, y, blink, state):
    body = struct.pack('<BffBB', quiz_id, x, y, blink, state)
    return DUMMY_HEADER + body

if __name__ == '__main__':
    start_pipe_server()
    # stop_event를 사용하는 경우 추가적인 로직 필요
    while True:
        time.sleep(1)
