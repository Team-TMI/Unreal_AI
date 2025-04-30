import cv2
import time
import struct
import pyautogui
import numpy as np
import win32file
import mediapipe as mp
from utils.face_utils import get_eye_openness, get_face_height
from utils.gaze_utils import map_calibrated_gaze
from utils.blink_detector import BlinkDetector
from utils.packet_utils import pack_eye_tracking_response_with_header

screen_w, screen_h = pyautogui.size()
blink_detector = BlinkDetector(threshold_ratio=0.5, blink_threshold=4)

def run_calibration(pipe):
    cap = cv2.VideoCapture(0)
    print("📍 칼리브레이션 모드 시작")
    
    margin = 50
    corner_points = [
        (margin, margin),
        (screen_w - margin, margin),
        (screen_w - margin, screen_h - margin),
        (margin, screen_h - margin)
    ]
    instructions = [
        "Top-Left", "Top-Right", "Bottom-Right", "Bottom-Left"
    ]

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    calibration_points = []
    calibration_eye_open_list = []
    calibration_step = 0

    def draw_cross(img, center, size=20, color=(0, 0, 255), thickness=2):
        cx, cy = center
        half = size // 2
        cv2.line(img, (cx - half, cy), (cx + half, cy), color, thickness)
        cv2.line(img, (cx, cy - half), (cx, cy + half), color, thickness)

    while calibration_step < 4:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        screen = np.ones((screen_h, screen_w, 3), dtype=np.uint8) * 255

        draw_cross(screen, corner_points[calibration_step], 30)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                left_iris = face_landmarks.landmark[468]
                right_iris = face_landmarks.landmark[473]
                eye_x = (left_iris.x + right_iris.x) / 2
                eye_y = (left_iris.y + right_iris.y) / 2

                # 🔥 현재 프레임의 eye_openness_normalized 계산
                eye_openness = get_eye_openness(landmarks)
                face_height = get_face_height(landmarks)
                eye_openness_normalized = eye_openness / face_height if face_height > 0 else 0

        cv2.imshow("Calibration", screen)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('w'):
            if results.multi_face_landmarks:
                calibration_points.append((eye_x, eye_y))
                calibration_eye_open_list.append(eye_openness_normalized)
                print(f"✅ {instructions[calibration_step]} 저장 완료")
                calibration_step += 1

        if key == ord('q'):
            print("🛑 캘리브레이션 강제 종료")
            break

    cap.release()
    cv2.destroyAllWindows()

    if calibration_eye_open_list:
        blink_detector.open_ref = np.mean(calibration_eye_open_list)
        print(f"✨ open_ref 설정 완료: {blink_detector.open_ref}")

    print("🎯 칼리브레이션 완료")
    return calibration_points  # ⭐반드시 리턴

def run_tracking(pipe, stop_event, calibration_points):
    cap = cv2.VideoCapture(0)
    print("🎯 미션 모드 시작")

    if calibration_points is None or len(calibration_points) != 4:
        print("❗ 캘리브레이션 데이터 부족. 기본값 사용")
        calibration_points = [(0.3, 0.3), (0.7, 0.3), (0.7, 0.7), (0.3, 0.7)]

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    prev_x, prev_y = None, None
    alpha = 0.3

    while not stop_event.is_set():
        
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                left_iris = face_landmarks.landmark[468]
                right_iris = face_landmarks.landmark[473]
                eye_x = (left_iris.x + right_iris.x) / 2
                eye_y = (left_iris.y + right_iris.y) / 2

                eye_openness = get_eye_openness(landmarks)
                face_height = get_face_height(landmarks)
                eye_openness_normalized = eye_openness / face_height if face_height > 0 else 0
                blink_state, blink_count = blink_detector.update(eye_openness_normalized, blink_detector.open_ref)

                gaze_x, gaze_y = map_calibrated_gaze(eye_x, eye_y, calibration_points, screen_w, screen_h, prev_x, prev_y, alpha)
                prev_x, prev_y = gaze_x, gaze_y
                

                try:
                    packet = pack_eye_tracking_response_with_header(
                        quiz_id=1,
                        x=float(gaze_x),
                        y=float(gaze_y),
                        blink=int(blink_state),
                        state=100
                    )
                    win32file.WriteFile(pipe, packet)
                    print(f"📤좌표 전송: ({gaze_x}, {gaze_y}) | blink={blink_state}")
                except Exception as e:
                    print(f"❌ Unreal 전송 실패: {e}")

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 미션 모드 종료")
