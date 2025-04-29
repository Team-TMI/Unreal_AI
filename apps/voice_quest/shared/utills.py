def get_or_create(game_db, session_id, quiz_id, player_id, quiz, answer):
    session = game_db.setdefault(session_id, {})
    info = session.setdefault(quiz_id, {
        "player_id": {},
        "quiz_id": quiz_id,
        "quiz" : quiz,
        "answer": answer
    })
    player = info["player_id"].setdefault(player_id, [])
    return player

def clear_session(game_db, session_id):
    if session_id in game_db:
        del game_db[session_id]

def save_reconstructed_audio(reconstructed_data, output_path="received_audio.wav"):
    """받은 reconstructed_data를 파일로 저장하는 함수"""
    with open(output_path, "wb") as f:
        f.write(reconstructed_data)
    print(f"[INFO] 오디오 저장 완료: {output_path}")