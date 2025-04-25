from shared.utills import get_or_create, clear_session

import struct

header_format = "<BH100sB"
quiz_notify_format = f"{header_format}3B"
wav_request_format = f"{header_format}6B1024s"

GAME_DB = {}

# quiz_llm = Quiz(
#     prompt_path="./prompts/quiz.prompt",
#     db_params=DB_PARAMS,
#     answer = answer
# )
# hint_llm = Hint(
#     prompt_path="./prompts/hint.prompt",
#     db_params=DB_PARAMS,
#     answer = answer
# )
def quiz_notify(raw_data, llm, answer):
    _, _, session_id, player_id, quiz_id, quiz_start, end = struct.unpack(quiz_notify_format, raw_data)
    
    if quiz_start == 1:
        print(f"[QuizNotify] 퀴즈 시작합니다.")
        quiz = llm.start_quiz()
        get_or_create(GAME_DB, session_id, quiz_id, player_id, quiz, answer)
        payload_size = 1 + 4 + 1 + 1 + 4 + len(quiz.encode("utf-8"))
        quiz_response = struct.pack(
            "<BH100sBBf?BI",
            5,
            payload_size,
            session_id,
            player_id,
            quiz_id,
            0.0,
            False,
            answer,
            len(quiz.encode("utf-8"))
        ) + quiz.encode("utf-8")
        return quiz_response
    
    else:
        print("[QuizNotify] 퀴즈 종료합니다.")
        clear_session(GAME_DB, session_id)
        return None

def wav_request(raw_data, llm, answer, reconstructor, stt_engine):

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

    if reconstructed_data:
        user_word = stt_engine.stt(reconstructed_data)

        hint = llm.invoke(user_word)
        success = hint['similarity'] > 0.92 # 임시로 했습니다
        payload_size = 1 + 4 + 1 + 1 + 4 + len(hint['response'].encode("utf-8"))
        hint_response = struct.pack(
            "<BH100sBBf?BI",
            5,
            payload_size,
            session_id,
            player_id,
            quiz_id,
            hint['similarity'],
            success,
            answer,
            len(hint['response'].encode("utf-8"))
        ) + hint['response'].encode("utf-8")
        return hint_response