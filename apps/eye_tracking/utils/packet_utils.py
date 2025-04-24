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

def pack_eye_tracking_response(quiz_id, width, height, x, y, blink, state):
    # Unreal로 전송할 좌표 패킷 직렬
    body = struct.pack('<BffffBB', quiz_id, width, height, x,y, blink, state)
    return DUMMY_HEADER + body

def unpack_eye_tracking_response(data):
    # 테스트용 역직렬화 함수???
    
    payload = data[HEADER_SIZE:]
    quiz_id, width, height, x, y, blink, state = struct.unpack('<BffffBB', payload)
    return {
        'QuizID': quiz_id,
        'Width': width,
        'Height': height,
        'X': x,
        'Y': y,
        'BBlink': blink,
        'State': state
    }


def dict_to_packet(data: dict) -> bytes:
    # Python에서 dict 형태의 gaze정보 Unreal 패킷으로 직렬화
    return pack_eye_tracking_response(
        quiz_id=data["quiz_id"],
        width=data["screen_w"],
        height=data["screen_h"],
        x=data["x"],
        y=data["y"],
        blink=data["blink"],
        state=data["state"]
    )