import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.main import (
        confirm_next_round_logic,
        generate_balanced_schedule,
        generate_room_code,
        join_player_logic,
        leave_room_logic,
        next_speaker_logic,
        reset_game_logic,
        resolve_round_votes,
        rooms,
        start_game_logic,
        start_pitch_logic,
        vote_logic,
    )
except ModuleNotFoundError:
    from main import (
        confirm_next_round_logic,
        generate_balanced_schedule,
        generate_room_code,
        join_player_logic,
        leave_room_logic,
        next_speaker_logic,
        reset_game_logic,
        resolve_round_votes,
        rooms,
        start_game_logic,
        start_pitch_logic,
        vote_logic,
    )


class TestRoomCodeGeneration(unittest.TestCase):
    def test_generate_room_code(self):
        rooms.clear()
        code = generate_room_code()
        self.assertEqual(len(code), 4)
        self.assertTrue(code.isalpha())
        self.assertTrue(code.isupper())


class TestBalancedSchedule(unittest.TestCase):
    def test_generate_balanced_schedule_empty(self):
        self.assertEqual(generate_balanced_schedule([]), [])

    def test_generate_balanced_schedule_even(self):
        players = ["P0", "P1", "P2", "P3"]
        schedule = generate_balanced_schedule(players)

        # For N=4 (even), there should be 4 rows
        self.assertEqual(len(schedule), 4)
        for row in schedule:
            self.assertEqual(len(row), 4)
            self.assertEqual(set(row), set(players))

        # Base row for N=4: indices [0, 1, 3, 2] -> ['P0', 'P1', 'P3', 'P2']
        self.assertEqual(schedule[0], ["P0", "P1", "P3", "P2"])

        # Check directed neighbor pairs in Williams Latin Square
        adjacent_pairs = set()
        for row in schedule:
            for i in range(len(row) - 1):
                adjacent_pairs.add((row[i], row[i + 1]))

        # For N=4, there are 4 * 3 = 12 directed pairs. Each pair should appear exactly once.
        self.assertEqual(len(adjacent_pairs), 12)

    def test_generate_balanced_schedule_odd(self):
        players = ["P0", "P1", "P2"]
        schedule = generate_balanced_schedule(players)

        # For N=3 (odd), there should be 2*N = 6 rows
        self.assertEqual(len(schedule), 6)
        for row in schedule:
            self.assertEqual(len(row), 3)
            self.assertEqual(set(row), set(players))

        # First block of N=3 rows
        self.assertEqual(schedule[0], ["P0", "P1", "P2"])
        self.assertEqual(schedule[1], ["P1", "P2", "P0"])
        self.assertEqual(schedule[2], ["P2", "P0", "P1"])

        # Second block of N=3 mirrored rows (from reversed base_row: [P2, P1, P0])
        self.assertEqual(schedule[3], ["P2", "P1", "P0"])
        self.assertEqual(schedule[4], ["P0", "P2", "P1"])
        self.assertEqual(schedule[5], ["P1", "P0", "P2"])

    def test_generate_balanced_schedule_dicts(self):
        player_dicts = [
            {"id": "id_0", "name": "Alice"},
            {"id": "id_1", "name": "Bob"},
            {"id": "id_2", "name": "Charlie"},
            {"id": "id_3", "name": "David"},
        ]
        schedule = generate_balanced_schedule(player_dicts)
        self.assertEqual(len(schedule), 4)
        self.assertEqual(schedule[0], ["id_0", "id_1", "id_3", "id_2"])


class TestJoinPlayerLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()

    def test_join_player_empty_name(self):
        with self.assertRaises(ValueError):
            join_player_logic("", "")

    def test_join_player_invalid_room_code(self):
        with self.assertRaises(ValueError):
            join_player_logic("INVALID123", "Alice")

    def test_join_player_creates_room_and_assigns_host(self):
        room, pid, err = join_player_logic("", "Alice")
        self.assertIsNone(err)
        self.assertIn(room["code"], rooms)
        self.assertEqual(len(room["players"]), 1)
        self.assertEqual(room["players"][0]["name"], "Alice")
        self.assertTrue(room["players"][0]["isHost"])
        self.assertEqual(room["hostId"], pid)

    def test_join_player_duplicate_name(self):
        room, _, _ = join_player_logic("", "Alice")
        with self.assertRaises(ValueError):
            join_player_logic(room["code"], "alice")

    def test_rejoin_existing_player_updates_name(self):
        room, pid, _ = join_player_logic("", "Alice")
        room, pid2, _ = join_player_logic(room["code"], "Alice Renamed", player_id=pid)
        self.assertEqual(pid, pid2)
        self.assertEqual(len(room["players"]), 1)
        self.assertEqual(room["players"][0]["name"], "Alice Renamed")


class TestStartGameLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()
        self.room, self.p1, _ = join_player_logic("", "Player 1")
        self.code = self.room["code"]
        _, self.p2, _ = join_player_logic(self.code, "Player 2")

    def test_start_game_room_not_found(self):
        with self.assertRaises(ValueError):
            start_game_logic("NONEXISTENT", self.p1)

    def test_start_game_non_host(self):
        _, p3, _ = join_player_logic(self.code, "Player 3")
        with self.assertRaises(ValueError):
            start_game_logic(self.code, self.p2)

    def test_start_game_insufficient_players(self):
        # Only 2 players in room
        with self.assertRaises(ValueError):
            start_game_logic(self.code, self.p1)

    def test_start_game_success(self):
        _, p3, _ = join_player_logic(self.code, "Player 3")
        room, err = start_game_logic(self.code, self.p1)
        self.assertIsNone(err)
        self.assertEqual(room["status"], "pitching")
        self.assertEqual(room["roundNumber"], 1)
        self.assertEqual(len(room["schedule"]), 6)  # N=3 (odd) -> 6 rows
        self.assertEqual(room["totalRounds"], 6)
        self.assertEqual(room["speakerOrder"], room["schedule"][0])
        self.assertTrue(len(room["currentProblem"]) > 0)
        self.assertEqual(len(room["currentWords"]), 1)


class TestPitchPhaseLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()
        self.room, self.p1, _ = join_player_logic("", "Player 1")
        self.code = self.room["code"]
        _, self.p2, _ = join_player_logic(self.code, "Player 2")
        _, self.p3, _ = join_player_logic(self.code, "Player 3")
        start_game_logic(self.code, self.p1)

    def test_start_pitch_invalid_status(self):
        self.room["status"] = "waiting"
        with self.assertRaises(ValueError):
            start_pitch_logic(self.code, self.p1)

    def test_start_pitch_wrong_speaker(self):
        first_speaker = self.room["speakerOrder"][0]
        wrong_speaker = [p for p in [self.p1, self.p2, self.p3] if p != first_speaker][0]
        with self.assertRaises(ValueError):
            start_pitch_logic(self.code, wrong_speaker)

    def test_start_pitch_success(self):
        first_speaker = self.room["speakerOrder"][0]
        room = start_pitch_logic(self.code, first_speaker)
        self.assertEqual(room["pitchState"], "pitching")
        self.assertIsNotNone(room["pitchStartTime"])

    def test_next_speaker_wrong_speaker(self):
        first_speaker = self.room["speakerOrder"][0]
        wrong_speaker = [p for p in [self.p1, self.p2, self.p3] if p != first_speaker][0]
        with self.assertRaises(ValueError):
            next_speaker_logic(self.code, wrong_speaker)

    def test_next_speaker_advance_and_transition_to_voting(self):
        # 3 players in round 1
        s1 = self.room["speakerOrder"][0]
        s2 = self.room["speakerOrder"][1]
        s3 = self.room["speakerOrder"][2]

        start_pitch_logic(self.code, s1)
        next_speaker_logic(self.code, s1)
        self.assertEqual(self.room["currentSpeakerIndex"], 1)
        self.assertEqual(self.room["pitchState"], "preparing")

        start_pitch_logic(self.code, s2)
        next_speaker_logic(self.code, s2)
        self.assertEqual(self.room["currentSpeakerIndex"], 2)

        start_pitch_logic(self.code, s3)
        next_speaker_logic(self.code, s3)
        # All speakers done -> transition to voting
        self.assertEqual(self.room["status"], "voting")
        self.assertEqual(self.room["votes"], {})


class TestVotingLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()
        self.room, self.p1, _ = join_player_logic("", "Player 1")
        self.code = self.room["code"]
        _, self.p2, _ = join_player_logic(self.code, "Player 2")
        _, self.p3, _ = join_player_logic(self.code, "Player 3")
        start_game_logic(self.code, self.p1)
        self.room["status"] = "voting"

    def test_vote_self_vote_fails(self):
        with self.assertRaises(ValueError):
            vote_logic(self.code, self.p1, self.p1)

    def test_vote_toggle(self):
        vote_logic(self.code, self.p1, self.p2)
        self.assertEqual(self.room["votes"].get(self.p1), self.p2)
        # Toggle off
        vote_logic(self.code, self.p1, self.p2)
        self.assertNotIn(self.p1, self.room["votes"])

    def test_vote_resolution_and_talent_bonus(self):
        # p1 votes for p2
        # p2 votes for p3
        # p3 votes for p2 -> p2 gets 2 votes (winner), p3 gets 1 vote
        vote_logic(self.code, self.p1, self.p2)
        vote_logic(self.code, self.p2, self.p3)
        # Final vote triggers resolve_round_votes
        vote_logic(self.code, self.p3, self.p2)

        self.assertEqual(self.room["status"], "round_result")
        res = self.room["lastRoundResult"]
        self.assertEqual(res["roundWinnerIds"], [self.p2])
        self.assertEqual(res["maxVotes"], 2)

        # Check player details:
        # p2 received 2 votes + 0 bonus = 2 coins (total 2)
        # p1 received 0 votes + 1 talent bonus (voted for p2, the winner) = 1 coin (total 1)
        # p3 received 1 vote + 0 bonus = 1 coin (total 1)
        details = res["playerDetails"]
        self.assertEqual(details[self.p2]["votesReceived"], 2)
        self.assertEqual(details[self.p2]["talentBonus"], 0)
        self.assertEqual(details[self.p1]["talentBonus"], 1)
        self.assertEqual(details[self.p3]["votesReceived"], 1)

    def test_vote_resolution_tie(self):
        # p1 votes for p2
        # p2 votes for p1
        # p3 votes for p1 -> tie if p3 votes for p2? No, p1 gets 2, p2 gets 1.
        # For a tie: p1 votes p2, p2 votes p3, p3 votes p1 -> each gets 1 vote (max 1 vote)
        vote_logic(self.code, self.p1, self.p2)
        vote_logic(self.code, self.p2, self.p3)
        vote_logic(self.code, self.p3, self.p1)

        res = self.room["lastRoundResult"]
        self.assertEqual(set(res["roundWinnerIds"]), {self.p1, self.p2, self.p3})
        self.assertEqual(res["maxVotes"], 1)
        # Everyone voted for a winner, so everyone gets 1 received + 1 bonus = 2 coins
        for pid in [self.p1, self.p2, self.p3]:
            self.assertEqual(res["playerDetails"][pid]["talentBonus"], 1)


class TestConfirmNextRoundAndEndGame(unittest.TestCase):
    def setUp(self):
        rooms.clear()
        self.room, self.p1, _ = join_player_logic("", "Player 1")
        self.code = self.room["code"]
        _, self.p2, _ = join_player_logic(self.code, "Player 2")
        _, self.p3, _ = join_player_logic(self.code, "Player 3")
        _, self.p4, _ = join_player_logic(self.code, "Player 4")
        start_game_logic(self.code, self.p1)
        # N=4 -> totalRounds = 4

    def test_confirm_next_round_partial(self):
        self.room["status"] = "round_result"
        confirm_next_round_logic(self.code, self.p1)
        self.assertEqual(self.room["status"], "round_result")
        self.assertTrue(self.room["players"][0]["confirmedNext"])
        self.assertFalse(self.room["players"][1]["confirmedNext"])

    def test_full_game_lifecycle_to_ended(self):
        for round_num in range(1, 5):
            self.assertEqual(self.room["roundNumber"], round_num)
            self.assertEqual(self.room["status"], "pitching")
            self.assertEqual(self.room["speakerOrder"], self.room["schedule"][round_num - 1])

            # Pitch phase
            for sp_id in self.room["speakerOrder"]:
                start_pitch_logic(self.code, sp_id)
                next_speaker_logic(self.code, sp_id)

            self.assertEqual(self.room["status"], "voting")

            # Voting phase (p1: p2, p2: p3, p3: p4, p4: p1)
            vote_logic(self.code, self.p1, self.p2)
            vote_logic(self.code, self.p2, self.p3)
            vote_logic(self.code, self.p3, self.p4)
            vote_logic(self.code, self.p4, self.p1)

            self.assertEqual(self.room["status"], "round_result")

            # Confirm next round
            for p in self.room["players"]:
                confirm_next_round_logic(self.code, p["id"])

        # After round 4 confirmation -> Game status = "ended"
        self.assertEqual(self.room["status"], "ended")
        game_res = self.room["lastGameResult"]
        self.assertIsNotNone(game_res)
        self.assertTrue(len(game_res["topWinners"]) > 0)
        self.assertEqual(len(game_res["standings"]), 4)


class TestResetGameLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()
        self.room, self.p1, _ = join_player_logic("", "Player 1")
        self.code = self.room["code"]
        _, self.p2, _ = join_player_logic(self.code, "Player 2")
        _, self.p3, _ = join_player_logic(self.code, "Player 3")
        start_game_logic(self.code, self.p1)

    def test_reset_game_non_host_fails(self):
        with self.assertRaises(ValueError):
            reset_game_logic(self.code, self.p2)

    def test_reset_game_success(self):
        room = reset_game_logic(self.code, self.p1)
        self.assertEqual(room["status"], "waiting")
        self.assertEqual(room["roundNumber"], 1)
        self.assertEqual(room["speakerOrder"], [])
        self.assertEqual(room["schedule"], [])
        self.assertEqual(room["currentProblem"], "")
        self.assertEqual(room["currentWords"], [])
        for p in room["players"]:
            self.assertEqual(p["score"], 0)
            self.assertFalse(p["confirmedNext"])


class TestLeaveRoomLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()

    def test_leave_room_not_found(self):
        with self.assertRaises(ValueError):
            leave_room_logic("NONEXISTENT", "p1")

    def test_leave_room_player_not_found(self):
        room, p1, _ = join_player_logic("", "Player 1")
        with self.assertRaises(ValueError):
            leave_room_logic(room["code"], "NONEXISTENT")

    def test_leave_room_regular_player(self):
        room, p1, _ = join_player_logic("", "Player 1")
        code = room["code"]
        _, p2, _ = join_player_logic(code, "Player 2")

        res = leave_room_logic(code, p2)
        self.assertFalse(res["room_closed"])
        self.assertEqual(len(res["room"]["players"]), 1)
        self.assertEqual(res["room"]["players"][0]["id"], p1)

    def test_leave_room_host_reassigns_new_host(self):
        room, p1, _ = join_player_logic("", "Player 1")
        code = room["code"]
        _, p2, _ = join_player_logic(code, "Player 2")

        res = leave_room_logic(code, p1)
        self.assertFalse(res["room_closed"])
        self.assertEqual(len(res["room"]["players"]), 1)
        self.assertEqual(res["room"]["players"][0]["id"], p2)
        self.assertTrue(res["room"]["players"][0]["isHost"])
        self.assertEqual(res["room"]["hostId"], p2)

    def test_leave_room_last_player_closes_room(self):
        room, p1, _ = join_player_logic("", "Player 1")
        code = room["code"]

        res = leave_room_logic(code, p1)
        self.assertTrue(res["room_closed"])
        self.assertNotIn(code, rooms)


if __name__ == "__main__":
    unittest.main()
