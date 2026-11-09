import json
import random
from pathlib import Path


TOTAL_STAGES = 10
QUESTION_DATA_PATH = Path(__file__).resolve().parent / "static" / "questions.json"
with QUESTION_DATA_PATH.open(encoding="utf-8") as question_file:
    QUESTION_DATA = json.load(question_file)["difficulties"]

DIFFICULTIES = {
    key: {"label": data["label"], "description": data["description"]}
    for key, data in QUESTION_DATA.items()
}
QUESTION_BANK = {
    key: tuple(data["questions"]) for key, data in QUESTION_DATA.items()
}
QUESTIONS = tuple(question for bank in QUESTION_BANK.values() for question in bank)


def create_game(score=0, question=None, difficulty="easy"):
    selected = question or random.choice(QUESTIONS)
    question_difficulty = difficulty if difficulty in QUESTION_BANK else "easy"
    distractors = [
        candidate
        for candidate in QUESTION_BANK[question_difficulty]
        if candidate["answer"] != selected["answer"]
    ]
    options = [selected, *random.sample(distractors, k=min(3, len(distractors)))]
    random.shuffle(options)
    choices = [
        {"letter": chr(ord("A") + index), "text": option["answer"]}
        for index, option in enumerate(options)
    ]
    correct_choice = next(
        choice["letter"]
        for choice, option in zip(choices, options)
        if option["answer"] == selected["answer"]
    )
    return {
        "question_id": selected.get("id", "custom"),
        "answer": selected["answer"].casefold(),
        "choices": choices,
        "correct_choice": correct_choice,
        "selected_choice": None,
        "category": selected["category"],
        "question": selected["question"],
        "clue": selected.get("clue", ""),
        "difficulty": difficulty,
        "hints": list(selected["hints"]),
        "revealed_hints": 0,
        "score": score,
        "status": "playing",
        "message": "เลือกคำตอบที่ถูกต้องจากตัวเลือกด้านล่าง",
    }


def create_player(name):
    return {
        "name": name.strip(),
        "screen": "stages",
        "score": 0,
        "unlocked_stage": 1,
        "completed_stages": [],
        "stage": None,
        "difficulty": None,
        "round": 0,
        "seen_questions": {difficulty: [] for difficulty in DIFFICULTIES},
        "game": None,
    }


def select_stage(player, stage_number):
    if not isinstance(stage_number, int) or not 1 <= stage_number <= TOTAL_STAGES:
        raise ValueError("ไม่พบด่านที่เลือก")
    if stage_number > player["unlocked_stage"]:
        raise ValueError("ผ่านด่านก่อนหน้าเพื่อปลดล็อกด่านนี้ก่อนนะ")
    player["stage"] = stage_number
    player["difficulty"] = None
    player["game"] = None
    player["screen"] = "difficulty"


def start_stage_game(player, difficulty):
    if player["screen"] != "difficulty" or player["stage"] is None:
        raise ValueError("เลือกด่านก่อนเริ่มเล่นนะ")
    if difficulty not in DIFFICULTIES:
        raise ValueError("เลือกระดับความยากที่มีให้เลือกนะ")

    seen = player["seen_questions"][difficulty]
    available = [question for question in QUESTION_BANK[difficulty] if question["id"] not in seen]
    if not available:
        seen.clear()
        available = list(QUESTION_BANK[difficulty])
    question = random.choice(available)
    seen.append(question["id"])

    player["difficulty"] = difficulty
    player["round"] += 1
    player["game"] = create_game(player["score"], question, difficulty)
    player["screen"] = "playing"


def public_player_state(player):
    if player is None:
        return {
            "screen": "welcome",
            "player_name": "",
            "score": 0,
            "unlocked_stage": 0,
            "completed_stages": [],
            "total_stages": TOTAL_STAGES,
            "difficulties": DIFFICULTIES,
            "difficulty_counts": {difficulty: len(bank) for difficulty, bank in QUESTION_BANK.items()},
        }

    state = {
        "screen": player["screen"],
        "player_name": player["name"],
        "score": player["score"],
        "unlocked_stage": player["unlocked_stage"],
        "completed_stages": player["completed_stages"],
        "total_stages": TOTAL_STAGES,
        "difficulty_counts": {difficulty: len(bank) for difficulty, bank in QUESTION_BANK.items()},
        "selected_stage": player["stage"],
        "difficulty": player["difficulty"],
        "difficulties": DIFFICULTIES,
        "round": player["round"],
    }
    if player["game"]:
        state.update(public_state(player["game"], player["round"]))
    return state


def apply_choice(game, choice):
    value = str(choice).strip().upper()
    if game["status"] != "playing":
        return {"message": "คำถามนี้ตอบไปแล้ว ไปด่านถัดไปกันเลย"}
    if value not in {option["letter"] for option in game["choices"]}:
        return {"message": "เลือกคำตอบ A, B, C หรือ D ก่อนนะ"}

    game["selected_choice"] = value
    if value == game["correct_choice"]:
        game["status"] = "won"
        game["score"] += 20
        game["message"] = f"ถูกต้อง! คำตอบคือ {game['answer'].upper()} +20 คะแนน"
    else:
        game["status"] = "lost"
        game["message"] = f"คำตอบที่ถูกคือ {game['answer'].upper()}"
    return {"message": game["message"]}


def reveal_hint(game):
    if game["status"] != "playing":
        return {"message": "รอบนี้จบแล้ว ไปคำถัดไปกันเลย"}
    if game["revealed_hints"] >= len(game["hints"]):
        return {"message": "เปิดคำใบ้ครบแล้ว ลองใช้เบาะแสที่มีดูนะ"}

    game["revealed_hints"] += 1
    game["score"] = max(0, game["score"] - 5)
    game["message"] = "เปิดคำใบ้เพิ่มแล้ว หัก 5 คะแนน"
    return {"message": game["message"]}


def public_state(game, round_number, result=None):
    show_answer = game["status"] in {"won", "lost"}
    return {
        "category": game["category"],
        "question": game["question"],
        "clue": game.get("clue", ""),
        "difficulty": game.get("difficulty", "easy"),
        "choices": game["choices"],
        "selected_choice": game["selected_choice"],
        "correct_choice": game["correct_choice"] if show_answer else None,
        "hints": game["hints"][: game["revealed_hints"]],
        "hints_remaining": len(game["hints"]) - game["revealed_hints"],
        "score": game["score"],
        "status": game["status"],
        "message": (result or {}).get("message", game["message"]),
        "answer": game["answer"].upper() if show_answer else None,
        "round": round_number,
    }

