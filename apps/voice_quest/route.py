from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.quiz_llm import Quiz
from models.hint_llm import Hint
from models.stt import STTEngine, WavReconstructor
from voice_request import quiz_notify, wav_request
from config import DB_PARAMS
import random

router = APIRouter()

stt_engine = STTEngine()
reconstructor = WavReconstructor()

def choice_answer():
    answer_list = ["달빛 연못", "연잎밥", "취당근", "개를리랄로 게를랄라 산", "말왕대벌", "깝파리", "양꼬도", "연잎 방방", "아리아리 아라리교", "아이스 부레옥잠 차"]
    return random.choice(answer_list)

@router.websocket("/voice_quest")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"WebSocket 연결됨")

    answer = choice_answer()
    quiz_llm = Quiz(
        prompt_path="./prompts/quiz.prompt",
        db_params=DB_PARAMS,
        answer=answer
    )
    hint_llm = Hint(
        prompt_path="./prompts/hint.prompt",
        db_params=DB_PARAMS,
        answer=answer
    )

    try:
        while True:
            raw_data = await websocket.receive_bytes()
            header_type = raw_data[0]

            if header_type == 3:  # QuizNotify
                response = quiz_notify(raw_data, quiz_llm, answer)
                await websocket.send_bytes(response)

            elif header_type == 4:  # WaveRequest
                result = wav_request(raw_data, hint_llm, answer, reconstructor, stt_engine)
                if result is not None:  
                    await websocket.send_bytes(result)

    except WebSocketDisconnect:
        print("연결 종료")