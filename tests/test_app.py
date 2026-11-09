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

    def test_winning_stage_unlocks_the_next_one(self):
        self.post_json("/api/start", {"name": "Mali"})
        self.post_json("/api/select-stage", {"stage": 1})
        game = self.post_json("/api/start-level", {"difficulty": "easy"}).get_json()
        game_data = next(iter(GAMES.values()))["game"]

        result = self.post_json("/api/guess", {"choice": game_data["correct_choice"]}).get_json()

        self.assertEqual(result["status"], "won")
        self.assertEqual(result["unlocked_stage"], 2)
        self.assertEqual(result["completed_stages"], [1])
        self.assertEqual(game["screen"], "playing")

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

    def test_name_is_not_stored_in_the_session_cookie(self):
        response = self.post_json("/api/start", {"name": "Private Name"})

        self.assertNotIn("Private Name", response.headers.get("Set-Cookie", ""))


if __name__ == "__main__":
    unittest.main()