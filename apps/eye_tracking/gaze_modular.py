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
    frame_count = 0
    calibration_step = 0

    while calibration_step < 4:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        screen = np.ones((screen_h, screen_w, 3), dtype=np.uint8) * 255

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_iris = face_landmarks.landmark[468]
                right_iris = face_landmarks.landmark[473]

                eye_x = (left_iris.x + right_iris.x) / 2
                eye_y = (left_iris.y + right_iris.y) / 2

                frame_count += 1

                if frame_count > 30:
                    calibration_points.append((eye_x, eye_y))
                    print(f"✅ {instructions[calibration_step]} 저장 완료")
                    calibration_step += 1
                    frame_count = 0

        cv2.imshow("Calibration", screen)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🎯 칼리브레이션 완료")


def run_tracking(pipe, stop_event):
    cap = cv2.VideoCapture(0)
    print("🎯 미션 모드 시작")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    blink_detector = BlinkDetector(threshold_ratio=0.5, blink_threshold=4)
    prev_x, prev_y = None, None
    alpha = 0.5

    while not stop_event.is_set():
        
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_iris = face_landmarks.landmark[468]
                right_iris = face_landmarks.landmark[473]

                eye_x = (left_iris.x + right_iris.x) / 2
                eye_y = (left_iris.y + right_iris.y) / 2

                gaze_x, gaze_y = map_calibrated_gaze(eye_x, eye_y, [(0.3, 0.3), (0.7, 0.3), (0.7, 0.7), (0.3, 0.7)], screen_w, screen_h, prev_x, prev_y, alpha)
                prev_x, prev_y = gaze_x, gaze_y

                packet = pack_eye_tracking_response_with_header(
                    quiz_id=100,
                    x=float(gaze_x),
                    y=float(gaze_y),
                    blink=0,
                    state=100
                )
                win32file.WriteFile(pipe, packet)
                print(f"📤 전송: ({gaze_x}, {gaze_y})")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 미션 모드 종료")