# packet_utils.py
import struct

HEADER_SIZE = 8
DUMMY_HEADER = b'\x00' * HEADER_SIZE

def pack_eye_tracking_response(quiz_id, x, y, blink, state):
    body = struct.pack('<BffBB', quiz_id, x, y, blink, state)
    return DUMMY_HEADER + body

# 🛑 여기에서 import 하지 마세요
# from unreal_pipe_sender import start_pipe_server ❌

# ✅ 아래처럼 __main__ 안에서만 import
if __name__ == '__main__':
    import time
    from unreal_pipe_sender import start_pipe_server  # 여기서만 import

    start_pipe_server()
    while True:
        time.sleep(1)
