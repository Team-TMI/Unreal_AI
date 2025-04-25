import struct

# Unreal과 협의한 패킷 구조 대응
# 참고 구조: FEyeTrackingResponse
#
# struct FEyeTrackingResponse {
#     FMessageHeader Header;
#     uint8 QuizID;
#     float Width;
#     float Height;
#     float X;
#     float Y;
#     uint8 BBlink;
#     uint8 State;
# }  

HEADER_SIZE = 8 #임의 값, UNREAL에 맞춰야 함
DUMMY_HEADER = b'\x00' * HEADER_SIZE

def pack_eye_tracking_request(quiz_id, width, height, start, end):
    # 칼리브레이션용
    body = struct.pack('<BffBB', quiz_id, width, height, start, end)
    return DUMMY_HEADER + body

def pack_eye_tracking_response(quiz_id, x, y, blink, state):
    body = struct.pack('<BffBB', quiz_id, x, y, blink, state)
    return DUMMY_HEADER + body

def pack_eye_tracking_notify(quiz_id, settingStart, start, end):
    body = struct.pack('<BBBB', quiz_id, settingStart, start, end)
    return DUMMY_HEADER + body