import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session

from game import (
    TOTAL_STAGES,
    apply_choice,
    create_player,
    public_player_state,
    reveal_hint,
    select_stage,
    start_stage_game,
)


BASE_DIR = Path(__file__).resolve().parent
GAMES = {}
app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "byte-buddy-local-development-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def _get_game():
    return GAMES.get(session.get("game_id"))


def _store_game(game):
    game_id = session.get("game_id") or secrets.token_urlsafe(24)
    GAMES[game_id] = game
    session["game_id"] = game_id


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/api/state")
def get_state():
    return jsonify(public_player_state(_get_game()))


@app.post("/api/start")
def start():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 20:
        return jsonify({"error": "ใส่ชื่อ 1-20 ตัวอักษรก่อนเริ่มเกมนะ"}), 400

    player = create_player(name)
    _store_game(player)
    return jsonify(public_player_state(player))


@app.post("/api/select-stage")
def choose_stage():
    player = _get_game()
    if player is None:
        return jsonify({"error": "เริ่มเกมและใส่ชื่อก่อนนะ"}), 400

    payload = request.get_json(silent=True) or {}
    try:
        stage_number = int(payload.get("stage", 0))
        select_stage(player, stage_number)
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(public_player_state(player))


@app.post("/api/start-level")
def choose_difficulty():
    player = _get_game()
    if player is None:
        return jsonify({"error": "เริ่มเกมและใส่ชื่อก่อนนะ"}), 400

    payload = request.get_json(silent=True) or {}
    try:
        start_stage_game(player, payload.get("difficulty", ""))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(public_player_state(player))


@app.post("/api/return-to-stages")
def return_to_stages():
    player = _get_game()
    if player is None:
        return jsonify({"error": "เริ่มเกมและใส่ชื่อก่อนนะ"}), 400
    player["screen"] = "stages"
    player["game"] = None
    return jsonify(public_player_state(player))


@app.post("/api/retry-stage")
def retry_stage():
    player = _get_game()
    if player is None or player["stage"] is None:
        return jsonify({"error": "เลือกด่านก่อนเริ่มเล่นนะ"}), 400
    player["screen"] = "difficulty"
    player["game"] = None
    return jsonify(public_player_state(player))


@app.post("/api/guess")
def guess():
    player = _get_game()
    if player is None or player["screen"] != "playing" or player["game"] is None:
        return jsonify({"error": "เลือกด่านและความยากก่อนเริ่มทายนะ"}), 400

    payload = request.get_json(silent=True) or {}
    game = player["game"]
    result = apply_choice(game, payload.get("choice", ""))
    player["score"] = game["score"]
    if game["status"] == "won":
        if player["stage"] not in player["completed_stages"]:
            player["completed_stages"].append(player["stage"])
        player["unlocked_stage"] = min(
            TOTAL_STAGES,
            max(player["unlocked_stage"], player["stage"] + 1),
        )
    return jsonify(public_player_state(player))


@app.post("/api/hint")
def hint():
    player = _get_game()
    if player is None or player["screen"] != "playing" or player["game"] is None:
        return jsonify({"error": "เลือกด่านและความยากก่อนเริ่มทายนะ"}), 400

    game = player["game"]
    reveal_hint(game)
    player["score"] = game["score"]
    return jsonify(public_player_state(player))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)