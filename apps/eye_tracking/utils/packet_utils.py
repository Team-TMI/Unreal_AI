# packet_utils.py
import struct

def pack_eye_tracking_response_with_header(quiz_id, x, y, blink, state):
    # Payload: EyeTrackingResponseMessage
    payload = struct.pack('<BffBB', quiz_id, x, y, blink, state)

    # Header: FMessageHeader
    message_type = 8  # EyeTrackingResponseMessage
    session_id = bytes([1, 0, 0, 0]) + bytes(96)  # 4 bytes ID + 96 bytes padding
    player_id = 1

    header_size = 1 + 2 + 100 + 1
    payload_size = header_size + len(payload)

    header = struct.pack('<BH100sB', message_type, payload_size, session_id, player_id)

    print(f"📦 실제 전송 패킷 사이즈: {len(header + payload)} (message size {payload_size})")

    return header + payload

# 🛑 여기는 테스트용 코드니까 배포할 때는 삭제하거나 주석 처리하는 게 좋음
# if __name__ == '__main__':
#     import time
#     from unreal_pipe_sender import start_pipe_server

#     start_pipe_server()
#     while True:
#         time.sleep(1)
