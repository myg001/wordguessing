import unittest
from unittest.mock import patch

from game import (
    DIFFICULTIES,
    QUESTION_BANK,
    TOTAL_STAGES,
    apply_choice,
    create_game,
    create_player,
    public_player_state,
    public_state,
    reveal_hint,
    select_stage,
    start_stage_game,
)


QUESTION = {
    "answer": "byte",
    "id": "byte",
    "category": "ทดสอบ",
    "question": "หน่วยข้อมูลดิจิทัลเรียกว่าอะไร?",
    "clue": "หน่วยข้อมูลดิจิทัล",
    "hints": ["มีสี่ตัวอักษร", "ขึ้นต้นด้วย B"],
}


class GameLogicTests(unittest.TestCase):
    def setUp(self):
        self.game = create_game(question=QUESTION)

    def test_game_has_four_choices_and_hides_correct_choice(self):
        state = public_state(self.game, 1)

        self.assertEqual([choice["letter"] for choice in state["choices"]], ["A", "B", "C", "D"])
        self.assertIsNone(state["correct_choice"])
        self.assertIsNone(state["answer"])

    def test_correct_choice_adds_score_and_wins(self):
        apply_choice(self.game, self.game["correct_choice"])

        state = public_state(self.game, 1)
        self.assertEqual(state["status"], "won")
        self.assertEqual(state["score"], 20)
        self.assertEqual(state["answer"], "BYTE")

    def test_wrong_choice_ends_round_without_points(self):
        wrong_choice = next(
            choice["letter"]
            for choice in self.game["choices"]
            if choice["letter"] != self.game["correct_choice"]
        )
        apply_choice(self.game, wrong_choice)

        state = public_state(self.game, 1)
        self.assertEqual(state["status"], "lost")
        self.assertEqual(state["answer"], "BYTE")
        self.assertEqual(state["score"], 0)

    def test_hint_costs_five_points_and_reveals_clue(self):
        self.game["score"] = 10
        reveal_hint(self.game)

        state = public_state(self.game, 1)
        self.assertEqual(state["score"], 5)
        self.assertEqual(state["hints"], ["มีสี่ตัวอักษร"])

    def test_invalid_choice_does_not_end_round(self):
        apply_choice(self.game, "Z")

        state = public_state(self.game, 1)
        self.assertEqual(state["status"], "playing")
        self.assertEqual(state["score"], 0)


class ProgressionTests(unittest.TestCase):
    def test_question_banks_are_separate_and_populated(self):
        self.assertEqual(set(QUESTION_BANK), set(DIFFICULTIES))
        self.assertTrue(all(len(bank) >= 5 for bank in QUESTION_BANK.values()))

    def test_locked_stage_cannot_be_selected(self):
        player = create_player("Byte")

        with self.assertRaises(ValueError):
            select_stage(player, 2)

    def test_stage_selection_opens_difficulty_screen(self):
        player = create_player("Byte")
        select_stage(player, 1)

        self.assertEqual(public_player_state(player)["screen"], "difficulty")
        self.assertEqual(public_player_state(player)["selected_stage"], 1)

    def test_questions_do_not_repeat_until_difficulty_bank_is_exhausted(self):
        player = create_player("Byte")
        answers = []

        with patch("game.random.choice", side_effect=lambda options: options[0]):
            for _ in QUESTION_BANK["easy"]:
                select_stage(player, 1)
                start_stage_game(player, "easy")
                answers.append(player["game"]["answer"])

        self.assertEqual(len(answers), len(set(answers)))
        self.assertEqual(player["difficulty"], "easy")

    def test_public_state_hides_answer_before_round_ends(self):
        player = create_player("Byte")
        select_stage(player, 1)
        start_stage_game(player, "hard")

        state = public_player_state(player)
        self.assertIsNone(state["answer"])
        self.assertEqual(state["difficulty"], "hard")
        self.assertEqual(state["total_stages"], TOTAL_STAGES)


if __name__ == "__main__":
    unittest.main()