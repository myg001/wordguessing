import unittest

from app import GAMES, app
from game import QUESTION_BANK


class GameApiTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        GAMES.clear()
        self.client = app.test_client()

    def post_json(self, path, payload):
        return self.client.post(path, json=payload)

    def test_new_player_sees_welcome_screen(self):
        response = self.client.get("/api/state")

        self.assertEqual(response.get_json()["screen"], "welcome")

    def test_player_can_start_select_stage_and_choose_difficulty(self):
        started = self.post_json("/api/start", {"name": "Mali"})
        stage = self.post_json("/api/select-stage", {"stage": 1})
        game = self.post_json("/api/start-level", {"difficulty": "hard"})
        state = game.get_json()

        self.assertEqual(started.get_json()["player_name"], "Mali")
        self.assertEqual(stage.get_json()["screen"], "difficulty")
        self.assertEqual(state["screen"], "playing")
        self.assertEqual(state["difficulty"], "hard")
        self.assertEqual(state["difficulty_counts"]["hard"], len(QUESTION_BANK["hard"]))
        self.assertIn(state["question"], [item["question"] for item in QUESTION_BANK["hard"]])
        self.assertIsNone(state["answer"])

    def test_stage_unlocks_after_five_answered_questions(self):
        self.post_json("/api/start", {"name": "Mali"})
        self.post_json("/api/select-stage", {"stage": 1})
        self.post_json("/api/start-level", {"difficulty": "easy"})

        for question_number in range(1, 6):
            game_data = next(iter(GAMES.values()))["game"]
            result = self.post_json(
                "/api/guess", {"choice": game_data["correct_choice"]}
            ).get_json()
            self.assertEqual(result["stage_questions_answered"], question_number)
            self.assertEqual(result["stage_finished"], question_number == 5)
            self.assertEqual(result["unlocked_stage"], 2 if question_number == 5 else 1)
            if question_number < 5:
                next_state = self.post_json("/api/next-question", {}).get_json()
                self.assertEqual(next_state["stage_question_number"], question_number + 1)

    def test_locked_stage_is_rejected(self):
        self.post_json("/api/start", {"name": "Mali"})

        response = self.post_json("/api/select-stage", {"stage": 2})

        self.assertEqual(response.status_code, 400)

    def test_retry_reuses_the_current_stage_difficulty(self):
        self.post_json("/api/start", {"name": "Mali"})
        self.post_json("/api/select-stage", {"stage": 1})
        self.post_json("/api/start-level", {"difficulty": "medium"})

        state = self.post_json("/api/retry-stage", {}).get_json()

        self.assertEqual(state["screen"], "playing")
        self.assertEqual(state["difficulty"], "medium")

    def test_wrong_answer_counts_and_allows_the_next_question(self):
        self.post_json("/api/start", {"name": "Mali"})
        self.post_json("/api/select-stage", {"stage": 1})
        self.post_json("/api/start-level", {"difficulty": "easy"})
        game = next(iter(GAMES.values()))["game"]
        wrong_choice = next(
            choice["letter"]
            for choice in game["choices"]
            if choice["letter"] != game["correct_choice"]
        )

        result = self.post_json("/api/guess", {"choice": wrong_choice}).get_json()
        next_question = self.post_json("/api/next-question", {}).get_json()

        self.assertEqual(result["stage_questions_answered"], 1)
        self.assertFalse(result["stage_finished"])
        self.assertEqual(result["unlocked_stage"], 1)
        self.assertEqual(next_question["stage_question_number"], 2)

    def test_name_is_not_stored_in_the_session_cookie(self):
        response = self.post_json("/api/start", {"name": "Private Name"})

        self.assertNotIn("Private Name", response.headers.get("Set-Cookie", ""))


if __name__ == "__main__":
    unittest.main()