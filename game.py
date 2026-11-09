import random


TOTAL_STAGES = 10
DIFFICULTIES = {
    "easy": {"label": "เริ่มต้น", "description": "อุปกรณ์และคำศัพท์พื้นฐาน"},
    "medium": {"label": "ท้าทาย", "description": "ระบบและแนวคิดคอมพิวเตอร์"},
    "hard": {"label": "ผู้เชี่ยวชาญ", "description": "เครือข่าย ความปลอดภัย และโค้ด"},
}

QUESTION_BANK = {
    "easy": (
        {
            "id": "keyboard",
            "answer": "keyboard",
            "category": "อุปกรณ์คอมพิวเตอร์",
            "question": "อุปกรณ์ที่ใช้พิมพ์ตัวอักษรและคำสั่งเข้าสู่คอมพิวเตอร์คืออะไร?",
            "clue": "อุปกรณ์รับข้อมูลที่มีปุ่มตัวอักษรให้กด",
            "hints": ["มีปุ่มเรียงกันหลายแถว", "ชื่อขึ้นต้นด้วยตัว K"],
        },
        {
            "id": "mouse",
            "answer": "mouse",
            "category": "อุปกรณ์คอมพิวเตอร์",
            "question": "อุปกรณ์ที่ใช้เลื่อนเคอร์เซอร์และคลิกเลือกสิ่งต่าง ๆ บนหน้าจอคืออะไร?",
            "clue": "อุปกรณ์ชี้ตำแหน่งที่มักมีปุ่มคลิกสองข้าง",
            "hints": ["บางรุ่นมีล้อเลื่อนตรงกลาง", "ชื่อเหมือนสัตว์ตัวเล็กที่ชอบชีส"],
        },
        {
            "id": "monitor",
            "answer": "monitor",
            "category": "อุปกรณ์คอมพิวเตอร์",
            "question": "อุปกรณ์แสดงภาพ ข้อความ และผลลัพธ์จากคอมพิวเตอร์เรียกว่าอะไร?",
            "clue": "หน้าจอที่ใช้ดูสิ่งต่าง ๆ จากเครื่องคอมพิวเตอร์",
            "hints": ["แสดงผลเป็นภาพและข้อความ", "ชื่อขึ้นต้นด้วยตัว M"],
        },
        {
            "id": "printer",
            "answer": "printer",
            "category": "อุปกรณ์คอมพิวเตอร์",
            "question": "อุปกรณ์ที่นำข้อความหรือภาพจากคอมพิวเตอร์ออกมาเป็นกระดาษคืออะไร?",
            "clue": "เปลี่ยนไฟล์ดิจิทัลให้กลายเป็นเอกสารบนกระดาษ",
            "hints": ["มักใช้หมึกหรือผงหมึก", "ชื่อขึ้นต้นด้วยตัว P"],
        },
        {
            "id": "folder",
            "answer": "folder",
            "category": "ไฟล์และข้อมูล",
            "question": "พื้นที่ที่ใช้จัดเก็บและจัดกลุ่มไฟล์ไว้ด้วยกันบนคอมพิวเตอร์เรียกว่าอะไร?",
            "clue": "ใช้แยกไฟล์เป็นหมวดหมู่ให้ค้นหาได้ง่าย",
            "hints": ["สร้างซ้อนกันเป็นชั้น ๆ ได้", "ชื่อเหมือนแฟ้มเอกสาร"],
        },
    ),
    "medium": (
        {
            "id": "processor",
            "answer": "processor",
            "category": "ฮาร์ดแวร์",
            "question": "ชิ้นส่วนใดทำหน้าที่ประมวลผลคำสั่งและข้อมูลของคอมพิวเตอร์?",
            "clue": "ชิปหลักที่ทำงานกับคำสั่งและข้อมูล",
            "hints": ["ติดตั้งอยู่บนเมนบอร์ด", "ชื่อย่อที่คุ้นกันคือ CPU"],
        },
        {
            "id": "browser",
            "answer": "browser",
            "category": "ซอฟต์แวร์",
            "question": "โปรแกรมที่ใช้เปิดเว็บไซต์และท่องอินเทอร์เน็ตเรียกว่าอะไร?",
            "clue": "โปรแกรมสำหรับเปิดดูเว็บเพจ",
            "hints": ["Chrome และ Firefox เป็นตัวอย่าง", "ชื่อขึ้นต้นด้วยตัว B"],
        },
        {
            "id": "database",
            "answer": "database",
            "category": "ข้อมูล",
            "question": "ระบบที่ใช้จัดเก็บและจัดระเบียบข้อมูลเพื่อให้ค้นหาได้สะดวกคืออะไร?",
            "clue": "คลังข้อมูลที่จัดระเบียบและค้นหาได้",
            "hints": ["เว็บไซต์ใช้เก็บข้อมูลผู้ใช้", "ชื่อประกอบด้วยคำว่า data และ base"],
        },
        {
            "id": "firewall",
            "answer": "firewall",
            "category": "ความปลอดภัย",
            "question": "ระบบใดช่วยกรองข้อมูลเครือข่ายเพื่อป้องกันการเชื่อมต่อที่ไม่ต้องการ?",
            "clue": "ด่านควบคุมข้อมูลเข้าออกเครือข่าย",
            "hints": ["ชื่อแปลตรงตัวได้ว่ากำแพงไฟ", "ทำงานตามกฎที่กำหนดไว้"],
        },
        {
            "id": "motherboard",
            "answer": "motherboard",
            "category": "ฮาร์ดแวร์",
            "question": "แผงวงจรหลักที่เชื่อมต่อ CPU หน่วยความจำ และอุปกรณ์ต่าง ๆ คืออะไร?",
            "clue": "แผงวงจรหลักที่เชื่อมอุปกรณ์ภายในเข้าด้วยกัน",
            "hints": ["ชิ้นส่วนอื่น ๆ มักติดตั้งหรือเชื่อมต่ออยู่กับสิ่งนี้", "ชื่อขึ้นต้นด้วยคำว่า mother"],
        },
    ),
    "hard": (
        {
            "id": "algorithm",
            "answer": "algorithm",
            "category": "การเขียนโปรแกรม",
            "question": "ชุดขั้นตอนที่เรียงลำดับเพื่อแก้ปัญหาหรือทำงานให้สำเร็จเรียกว่าอะไร?",
            "clue": "ขั้นตอนแก้ปัญหาที่เรียงลำดับไว้อย่างชัดเจน",
            "hints": ["ไม่จำเป็นต้องเขียนเป็นโค้ดเสมอไป", "ชื่อขึ้นต้นด้วยตัว A"],
        },
        {
            "id": "encryption",
            "answer": "encryption",
            "category": "ความปลอดภัย",
            "question": "การแปลงข้อมูลให้อ่านไม่ออกหากไม่มีรหัสหรือกุญแจที่ถูกต้องคืออะไร?",
            "clue": "การเข้ารหัสก่อนส่งหรือจัดเก็บข้อมูล",
            "hints": ["ช่วยปกป้องข้อมูลที่ส่งผ่านอินเทอร์เน็ต", "ชื่อขึ้นต้นด้วยตัว E"],
        },
        {
            "id": "bandwidth",
            "answer": "bandwidth",
            "category": "เครือข่าย",
            "question": "ค่าที่บอกความจุสูงสุดของการรับส่งข้อมูลบนเครือข่ายคืออะไร?",
            "clue": "ค่านี้บอกปริมาณข้อมูลที่ส่งผ่านเครือข่ายได้",
            "hints": ["มักวัดเป็นบิตต่อวินาที", "ชื่อขึ้นต้นด้วยคำว่า band"],
        },
        {
            "id": "virtualization",
            "answer": "virtualization",
            "category": "ระบบคอมพิวเตอร์",
            "question": "เทคนิคที่จำลองเครื่องหรือทรัพยากรคอมพิวเตอร์ให้ทำงานแยกจากฮาร์ดแวร์จริงเรียกว่าอะไร?",
            "clue": "ทำให้เครื่องจริงหนึ่งเครื่องจำลองเป็นหลายสภาพแวดล้อมได้",
            "hints": ["เครื่องเสมือนเป็นตัวอย่างของเทคนิคนี้", "ชื่อขึ้นต้นด้วย virtual"],
        },
        {
            "id": "authentication",
            "answer": "authentication",
            "category": "ความปลอดภัย",
            "question": "กระบวนการตรวจสอบว่าผู้ใช้เป็นบุคคลตามที่กล่าวอ้างเรียกว่าอะไร?",
            "clue": "ขั้นตอนยืนยันตัวตนก่อนอนุญาตให้เข้าใช้งาน",
            "hints": ["รหัสผ่านและลายนิ้วมือใช้ในกระบวนการนี้ได้", "ชื่อขึ้นต้นด้วยคำว่า auth"],
        },
    ),
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
            "difficulty_counts": {
                difficulty: len(bank) for difficulty, bank in QUESTION_BANK.items()
            },
        }

    state = {
        "screen": player["screen"],
        "player_name": player["name"],
        "score": player["score"],
        "unlocked_stage": player["unlocked_stage"],
        "completed_stages": player["completed_stages"],
        "total_stages": TOTAL_STAGES,
        "difficulty_counts": {
            difficulty: len(bank) for difficulty, bank in QUESTION_BANK.items()
        },
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
    if value not in {choice["letter"] for choice in game["choices"]}:
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

