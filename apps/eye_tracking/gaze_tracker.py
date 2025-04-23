import cv2
import mediapipe as mp
import pyautogui
import numpy as np

def run_gaze_estimation(q, show_face_mesh=False, stop_event=None):
    screen_w, screen_h = pyautogui.size()   # 현재 모니터 해상도
    cap = cv2.VideoCapture(0)               # 노트북 카메라 캡쳐
    print(f"Gaze Estimation, Camera resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    mp_face_mesh = mp.solutions.face_mesh                       # 얼굴 인식 클래스
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)    # 얼굴 메쉬 중 refine_landmarks 반영(홍채)

    if show_face_mesh:        # 얼굴 메쉬 불러올 때
        mp_drawing = mp.solutions.drawing_utils                 # 얼굴에 그리는 기능
        mp_drawing_styles = mp.solutions.drawing_styles         # 그리는 스타일 셋 가져옴
        cv2.namedWindow("Face Mesh View", cv2.WINDOW_NORMAL)    # "Face Mesh View" 창 열기

    cv2.namedWindow("Gaze Estimation", cv2.WINDOW_NORMAL)       # "Gaze Estimation" 창 열기

    calibration_step = 0            # 현재 보정 중인 코너
    calibration_complete = False    # 보정 완료 여부
    calibration_points = []         # 수집된 눈 위치 저장

    margin = 50         # 모서리 좌표 기준
    corner_points = [
        (margin, margin),  # top-left
        (screen_w - margin, margin),  # top-right
        (margin, screen_h - margin),  # bottom-left
        (screen_w - margin, screen_h - margin)  # bottom-right
    ]
    instructions = [    # 각 모서리 안내
        "Look at top-left corner and press 'w'",
        "Look at top-right corner and press 'w'",
        "Look at bottom-left corner and press 'w'",
        "Look at bottom-right corner and press 'w'"
    ]

    # 보간용 초기화
    prev_x, prev_y = None, None
    alpha = 0.5 # 부드러움 정도 (0.1 ~ 0.3 추천)

    while True:
        if stop_event and stop_event.is_set():  # Stop event가 실행되면
            print("stop_event 를 통한 루프 종료")
            break                               # 종료

        ret, frame = cap.read()                 # ret = 프레임 정상적으로 읽었는지 여부, frame = 영상데이터
        if not ret:                             # 정상적으로 못 읽으면
            break                               # 종료

        frame = cv2.flip(frame, 1)              # frame 의 이미지를 좌우 반전
        face_mesh_frame = frame.copy() if show_face_mesh else None  # 메쉬를 본다면, frame을 복사하여 저장

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환하여 저장
        results = face_mesh.process(rgb_frame)

        screen = np.ones((screen_h, screen_w, 3), dtype=np.uint8) * 255

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                if show_face_mesh and face_mesh_frame is not None:
                    mp_drawing.draw_landmarks(
                        image=face_mesh_frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
                    mp_drawing.draw_landmarks(
                        image=face_mesh_frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=1)
                    )
                left_iris = face_landmarks.landmark[468]
                right_iris = face_landmarks.landmark[473]
                nose_tip = face_landmarks.landmark[1]

                eye_x = (left_iris.x + right_iris.x) / 2
                eye_y = (left_iris.y + right_iris.y) / 2

                dx = eye_x - nose_tip.x
                dy = eye_y - nose_tip.y

                gaze_x = int((0.5 + dx * 5) * screen_w)
                gaze_y = int((0.5 + dy * 5) * screen_h)

                gaze_x = np.clip(gaze_x, 0, screen_w - 1)
                gaze_y = np.clip(gaze_y, 0, screen_h - 1)

                # cv2.circle(screen, (gaze_x, gaze_y), 20, (255, 0, 0), -1)
                if not stop_event.is_set():
                    q.put((gaze_x, gaze_y))# ✅ IPC로 전송

                if not calibration_complete:
                    if calibration_step < 4:
                        # 보정용 십자 표시
                        cv2.circle(screen, corner_points[calibration_step], 30, (0, 0, 255), -1)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        text = instructions[calibration_step]
                        (tw, th), _ = cv2.getTextSize(text, font, 0.8, 2)
                        tx = (screen_w - tw) // 2
                        ty = screen_h // 2
                        cv2.putText(screen, text, (tx, ty), font, 0.8, (0, 0, 0), 2)
                else:
                    # 눈 위치를 보정된 화면 좌표로 매핑
                    xs, ys = zip(*calibration_points)
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)

                    range_x = max_x - min_x
                    range_y = max_y - min_y

                    dx = eye_x
                    dy = eye_y

                    if range_x == 0 or range_y == 0:
                        mapped_x, mapped_y = screen_w // 2, screen_h // 2
                    else:
                        mapped_x = int((dx - min_x) / range_x * screen_w)
                        mapped_y = int((dy - min_y) / range_y * screen_h)

                    mapped_x = np.clip(mapped_x, 0, screen_w - 1)
                    mapped_y = np.clip(mapped_y, 0, screen_h - 1)

                    if prev_x is not None and prev_y is not None:   #처음 시작할 때 이전 좌표가 없기 때문에, 있을 때에만 실행
                        mapped_x = int(alpha * mapped_x + (1 - alpha) * prev_x) #좌표 = 조정값 * 위치 + (1-조정값) * 이전 값
                        mapped_y = int(alpha * mapped_y + (1 - alpha) * prev_y) 

                    prev_x, prev_y = mapped_x, mapped_y     # 이전 값 = 현재 값

                    cv2.circle(screen, (mapped_x, mapped_y), 20, (0, 0, 255), -1)
                    if not stop_event.is_set():
                        q.put((mapped_x, mapped_y))



        key = cv2.waitKey(1) & 0xFF
        if key == ord('w') and not calibration_complete and calibration_step < 4:
            calibration_points.append((eye_x, eye_y))
            calibration_step += 1
            if calibration_step == 4:
                calibration_complete = True

        if key == ord('q'):
            if stop_event is not None:
                print("🛑 Gaze Estimation 종료 신호 전송")
                stop_event.set()
            break

        cv2.imshow("Gaze Estimation", screen)
        if show_face_mesh and face_mesh_frame is not None:
            cv2.imshow("Face Mesh View", face_mesh_frame)

    cap.release()
    cv2.destroyAllWindows()