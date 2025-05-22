from shared.utills import get_or_create, clear_session, save_reconstructed_audio

import struct
import base64

header_format = "<BH100sB"
quiz_notify_format = f"{header_format}3B"
wav_request_format = f"{header_format}BBIBII1024s"
# wav_request_format = f"{header_format}BBIBII1024s"

GAME_DB = {}


def quiz_notify(raw_data, llm, answer):
    _, _, session_id, player_id, quiz_id, quiz_start, end = struct.unpack(quiz_notify_format, raw_data)
    if quiz_start == 1:
        print(f"[QuizNotify] 퀴즈 시작합니다.")
        quiz = llm.start_quiz()
        print("퀴즈 길이",len(quiz))
        print("퀴즈", quiz)
        get_or_create(GAME_DB, session_id, quiz_id, player_id, quiz, answer)
        payload_size = 1 + 2 + 100 + 1 + 1 + 4 + 1 + 4 + len(quiz.encode("utf-8"))
        quiz_response = struct.pack(
            "<BH100sBBfBI",                   # 수정된 포맷
            5,                                   # Header.Type
            payload_size,                        # Header.PayloadSize
            session_id if isinstance(session_id, bytes) else session_id.encode(),
            int(player_id),
            int(quiz_id),
            float(0.0),                          # Similarity (시작 시 0.0)
            int(0),                              # bSuccess → False (0)
            len(quiz.encode("utf-8"))            # MessageSize
        ) 

        print(f"pay load : {payload_size}")
        print(f"보내는 raw_data 길이 : {len(quiz_response)}")
        print(f"보내는 raw_data+문자 길이 : {len(quiz_response + quiz.encode('utf-8'))}")
        print(f"[QuizNotify] 데이터 보냈음")
        return quiz_response + quiz.encode("utf-8")
    
    else:
        print("[QuizNotify] 퀴즈 종료합니다.")
        clear_session(GAME_DB, session_id)
        return None

def wav_request(raw_data, llm, answer, reconstructor, stt_engine):
    print("[WaveRequest] 접속 성공")
    expected_size = struct.calcsize(wav_request_format)

    print(f"[raw_data]{raw_data}")
    print(f"Expected size: {struct.calcsize(wav_request_format)}")
    print(f"Received size: {len(raw_data)}")
    
    if len(raw_data) < expected_size:
        print(f"[raw_data]{raw_data}")
        print(f"[ERROR] wav_request: Expected {expected_size} bytes, but got {len(raw_data)} bytes")
        return None

    _, _, session_id, player_id, quiz_id, answer_start, index, fin, total_size, chunk_size, audio_data = struct.unpack(wav_request_format, raw_data)
    reconstructed_data = reconstructor.receive_packet(
        quiz_id=quiz_id,
        start=answer_start,
        index = index,
        fin = fin,
        total_size=total_size,
        chunk_size=chunk_size,
        raw_data=audio_data
    )
    print(f"start : {answer_start}, fin : {fin}")
    if not fin:
        return None
    
    if reconstructed_data:
        save_reconstructed_audio(reconstructed_data)
        base64_data = base64.b64encode(reconstructed_data).decode('utf-8')
        user_word = stt_engine.stt(base64_data)

        hint = llm.invoke(user_word)
        success = hint['contain']
        payload_size = 1 + 2 + 100 + 1 + 1 + 4 + 1 + 4 + len(hint['response'].encode("utf-8"))
        hint_response = struct.pack(
            "<BH100sBBfBI",                    # 수정된 포맷 (Answer 없음)
            5,                                    # Header.Type (WaveResponse)
            payload_size,
            session_id if isinstance(session_id, bytes) else session_id.encode(),
            int(player_id),
            int(quiz_id),
            float(hint['similarity']),
            int(success),
            len(hint['response'].encode("utf-8")) # MessageSize
        ) 
        print(f"[성공했나?] {success}, 유사하나? {hint['similarity']}")
        print(f"pay load : {payload_size}")
        print(f"보내는 raw_data 길이 : {len(hint_response)}")
        print(f"보내는 raw_data+문자 길이 : {len(hint_response + hint['response'].encode('utf-8'))}")
        print(f"[QuizNotify] 데이터 보냈음")
        return hint_response + hint['response'].encode("utf-8")