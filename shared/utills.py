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