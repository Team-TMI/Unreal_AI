import struct

HEADER_SIZE = 8
DUMMY_HEADER = b'\x00' * HEADER_SIZE

def pack_eye_tracking_response(quiz_id, x, y, blink, state):
    body = struct.pack('<BffBB', quiz_id, x, y, blink, state)
    return DUMMY_HEADER + body
