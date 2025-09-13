"""
KInARow.py
Author: Sharma, Aarush

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
This version implements the persona of Chaddington “Bruh” Balding III,
with move ordering, Zobrist hashing, and two features:
  1. If the opponent says "Tell me how you did that", the agent explains its search stats.
  2. If the opponent says "What's your take on the game so far?", the agent tells a game narrative.
"""

import math
import random
import copy
import time

from src.agent_base import KAgent
from src.game_types import State, Game_Type
from src.winTesterForK import winTesterForK

AUTHOR = "Aarush Sharma"


class OurAgent(KAgent):
    def __init__(self, twin=False):
        self.twin = twin
        self.nickname = "Bruh"
        if twin:
            self.nickname += "2"
        self.long_name = "Chaddington 'Bruh' Balding III"
        if twin:
            self.long_name += " II"
        # Persona info: Over-the-top fratccent.
        self.persona = "Chaddington 'Bruh' Balding III"
        self.voice_info = {"Chrome": 10, "Firefox": 2, "other": 0}
        self.playing = None  # "X" or "O", set in prepare()
        self.current_game_type = None
        self.llm_enabled = False # Controls if the LLM API can be used.
        self.gemini_model = None # To hold the initialized Gemini model.

        # Dialog/instrumentation tracking.
        self.turn_count = 0
        self.my_past_utterances = []
        self.opponent_past_utterances = []
        self.game_state_history = []  # Stores board states (copies) over the game.
        self.alpha_beta_cutoffs_this_turn = 0
        self.num_static_evals_this_turn = 0
        self.last_move_time = 0.0  # Time spent on the last move.

        # Zobrist hashing data.
        self.zobrist_keys = None  # (r, c, token) -> random 64-bit int
        self.transposition_table = {}  # Map from state hash to evaluation value
        self.zobrist_write_count = 0
        self.zobrist_read_attempt_count = 0
        self.zobrist_hit_count = 0

    def introduce(self):
        # Slow, drawn-out introduction with frat swagger.
        intro = (
            "Uhhh... yo, what's up, my dudes? I'm Chaddington 'Bruh' Balding III, \n"
            "the legendary Prez of Pi Eta Epsilon—y'know, the one and only party \n"
            "icon on campus. I'm here to wreck this Connect 5 game like it's a \n"
            "pre-game warmup. Let's get it, brah!\n"
        )
        if self.twin:
            intro += "And oh, check it—I got my twin here too, double trouble and all that.\n"
        return intro

    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move=0.1,
        utterances_matter=True,
        apis_ok=True, # New parameter to allow external APIs.
    ):
        self.current_game_type = game_type
        self.playing = what_side_to_play
        self.llm_enabled = apis_ok
        self.init_zobrist()
        return "OK"

    def init_zobrist(self):
        """
        Initialize Zobrist keys for each board cell for tokens 'X' and 'O'.
        """
        n = self.current_game_type.n  # number of rows
        m = self.current_game_type.m  # number of columns
        self.zobrist_keys = {}
        for r in range(n):
            for c in range(m):
                for token in ["X", "O"]:
                    self.zobrist_keys[(r, c, token)] = random.getrandbits(64)
        self.transposition_table = {}
        self.zobrist_write_count = 0
        self.zobrist_read_attempt_count = 0
        self.zobrist_hit_count = 0

    def compute_zobrist(self, state):
        """
        Compute the Zobrist hash for the given state.
        """
        h = 0
        board = state.board
        for r in range(len(board)):
            for c in range(len(board[0])):
                token = board[r][c]
                if token in ["X", "O"]:
                    h ^= self.zobrist_keys.get((r, c, token), 0)
        return h

    def make_move(
        self,
        current_state,
        current_remark,
        time_limit=1000,
        autograding=False,
        use_alpha_beta=True,
        use_zobrist_hashing=False,
        max_ply=3,
        special_static_eval_fn=None,
    ):
        """
        Uses minimax search with alpha-beta pruning
        to choose a move, then generates an in-character utterance.
        Also measures and stores time spent on the move.
        """
        self.turn_count += 1
        if current_remark:
            self.opponent_past_utterances.append(current_remark)

        # Record starting time.
        start_time = time.time()

        # Reset per-turn instrumentation.
        self.alpha_beta_cutoffs_this_turn = 0
        self.num_static_evals_this_turn = 0

        alpha = -math.inf
        beta = math.inf
        best_move = None
        if self.playing == "X":
            best_value = -math.inf
        else:
            best_value = math.inf

        available_moves = self.get_available_moves(current_state)
        # Order moves by evaluating child states (move ordering).
        ordered_children = []
        for move in available_moves:
            child_state = self.apply_move(current_state, move)
            child_eval = self.static_eval(child_state)
            ordered_children.append((move, child_state, child_eval))
        if self.playing == "X":
            ordered_children.sort(key=lambda x: x[2], reverse=True)
        else:
            ordered_children.sort(key=lambda x: x[2])

        for move, candidate_state, child_eval in ordered_children:
            value = self.minimax(
                candidate_state,
                max_ply - 1,
                use_alpha_beta,
                alpha,
                beta,
                use_zobrist=use_zobrist_hashing,
                order_moves=True,
            )
            if self.playing == "X" and value > best_value:
                best_value = value
                best_move = move
                alpha = max(alpha, value)
            elif self.playing == "O" and value < best_value:
                best_value = value
                best_move = move
                beta = min(beta, value)
            if use_alpha_beta and beta <= alpha:
                self.alpha_beta_cutoffs_this_turn += 1
                break

        if best_move is None:
            if not available_moves:
                raise ValueError("No valid moves available!")
            best_move = random.choice(available_moves)

        new_state = self.apply_move(current_state, best_move)
        # Record end time and compute move time.
        end_time = time.time()
        self.last_move_time = end_time - start_time

        # Append the new state to our game history.
        self.game_state_history.append(copy.deepcopy(new_state))

        # Generate an utterance (this function now checks for special opponent commands).
        new_remark = self.generate_utterance(
            best_move, best_value, current_remark, new_state
        )
        self.my_past_utterances.append(new_remark)
        return [[best_move, new_state], new_remark]

    def minimax(
        self,
        state,
        depth_remaining,
        pruning=False,
        alpha=None,
        beta=None,
        use_zobrist=False,
        order_moves=True,
    ):
        """
        Minimax search with alpha-beta pruning, move ordering, and Zobrist hashing.
        """
        if depth_remaining == 0 or self.is_terminal(state):
            self.num_static_evals_this_turn += 1
            return self.static_eval(state)

        if use_zobrist:
            h = self.compute_zobrist(state)
            self.zobrist_read_attempt_count += 1
            if h in self.transposition_table:
                self.zobrist_hit_count += 1
                return self.transposition_table[h]

        if pruning:
            if alpha is None:
                alpha = -math.inf
            if beta is None:
                beta = math.inf

        current_player = state.whose_move
        moves = self.get_available_moves(state)
        child_list = []
        for move in moves:
            child_state = self.apply_move(state, move)
            eval_value = self.static_eval(child_state)
            child_list.append((move, child_state, eval_value))
        if order_moves:
            if current_player == "X":
                child_list.sort(key=lambda x: x[2], reverse=True)
            else:
                child_list.sort(key=lambda x: x[2])

        if current_player == "X":
            best_value = -math.inf
            for move, child_state, _ in child_list:
                value = self.minimax(
                    child_state,
                    depth_remaining - 1,
                    pruning,
                    alpha,
                    beta,
                    use_zobrist,
                    order_moves,
                )
                best_value = max(best_value, value)
                if pruning:
                    alpha = max(alpha, best_value)
                    if beta <= alpha:
                        self.alpha_beta_cutoffs_this_turn += 1
                        break
        else:
            best_value = math.inf
            for move, child_state, _ in child_list:
                value = self.minimax(
                    child_state,
                    depth_remaining - 1,
                    pruning,
                    alpha,
                    beta,
                    use_zobrist,
                    order_moves,
                )
                best_value = min(best_value, value)
                if pruning:
                    beta = min(beta, best_value)
                    if beta <= alpha:
                        self.alpha_beta_cutoffs_this_turn += 1
                        break

        if use_zobrist:
            self.transposition_table[h] = best_value
            self.zobrist_write_count += 1

        return best_value

    def _generate_llm_utterance(self, best_move, best_value, opponent_remark):
        """Generates an utterance using the Gemini LLM if available."""
        if not self.llm_enabled:
            return None

        try:
            # Conditional import to avoid issues when APIs are not allowed.
            import google.generativeai as genai
            from src.secrets import GOOGLE_API_KEY  # Import the key from your new file

            # It's good practice to only configure this once.
            if not self.gemini_model:
                genai.configure(api_key=GOOGLE_API_KEY)  # Configure using the imported key
                self.gemini_model = genai.GenerativeModel('gemini-pro')

            row, col = best_move
            
            # Construct a detailed prompt for the LLM
            prompt = (
                f"You are Chaddington 'Bruh' Balding III, an over-the-top, boastful, but ultimately good-natured frat bro. "
                f"You are playing a game of {self.current_game_type.k}-in-a-row. Your persona is paramount. Use slang like 'brah', 'dude', 'no cap', 'let's gooo', etc. "
                f"Generate a short, in-character utterance (1-2 sentences) for your turn.\n\n"
                f"Game Context:\n"
                f"- Your move: Placed a piece at ({row}, {col}).\n"
                f"- Your evaluation: The game state value is {best_value:.2f}. (A high positive value is very good for you, 'X'. A high negative value is bad.)\n"
                f"- Opponent's last remark: \"{opponent_remark if opponent_remark else 'None'}\"\n\n"
                f"Based on this, say something confident and funny. If your evaluation is high, be extra boastful. If it's low, be dismissive of the opponent's temporary advantage. If the opponent said something, you can react to it."
            )
            
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()

        except (ImportError, Exception) as e:
            # Add a check for FileNotFoundError in case secrets.py is missing
            if isinstance(e, FileNotFoundError):
                print("LLM utterance generation failed: secrets.py not found.")
            else:
                print(f"LLM utterance generation failed: {e}")
            self.llm_enabled = False # Disable for future turns to avoid repeated errors.
            return None


    def generate_utterance(self, best_move, best_value, opponent_remark, new_state):
        """
        Generates an utterance in character. It first checks for special commands,
        then attempts to use an LLM if enabled, and finally falls back to a
        rule-based system.
        """
        # Check for special opponent commands first (case-insensitive).
        lower_remark = opponent_remark.lower() if opponent_remark else ""

        if "tell me how you did that" in lower_remark:
            return (
                "Aight, brah, you wanna see the stats? No cap. Here's the breakdown:\n"
                f"- Static evaluations: I ran the numbers on {self.num_static_evals_this_turn} board states.\n"
                f"- Alpha-Beta Pruning: Saved time with {self.alpha_beta_cutoffs_this_turn} cutoffs. That's, like, peak efficiency.\n"
                f"- Zobrist Hashing: My transposition table had {self.zobrist_hit_count} hits out of {self.zobrist_read_attempt_count} reads. Stored {self.zobrist_write_count} new states.\n"
                f"- Total Time: The whole thing took me {self.last_move_time:.4f} seconds. Let's gooo!"
            )

        if "what's your take on the game so far" in lower_remark:
            summary = f"Yo, so you want the game recap? Bruh, it's been epic. We're {self.turn_count} turns in.\n"
            if best_value > 100:
                summary += "From where I'm sittin', this board is lookin' like a straight-up masterpiece painted by yours truly. Every move has been a step towards total ownage.\n"
                prediction = "My prediction? Victory is, like, basically a done deal. Just watch, dude."
            elif best_value < -100:
                summary += "NGL, you've put up a bit of a fight, kinda like that one pledge who tried to out-party me. Cute.\n"
                prediction = "You might think you're ahead, but I'm about to flip this board like a pancake. I got this."
            else:
                summary += "It's been a solid back-and-forth, like a good game of beer pong. Respect.\n"
                prediction = "It's still anyone's game, but, like, c'mon... it's me. My prediction is I'm gonna clutch this win."
            return summary + " " + prediction

        # Attempt to use LLM for a dynamic, creative utterance.
        llm_remark = self._generate_llm_utterance(best_move, best_value, opponent_remark)
        if llm_remark:
            return llm_remark

        # Fallback to rule-based utterances if LLM is disabled or fails.
        row, col = best_move
        utterance = f"Uhhh… yo, I’m droppin’ my piece at ({row}, {col}). "
        if best_value > 500:
            utterance += "Whoooa, scuse me, brah…that move’s like, the sound of victory bubblin’ in my gut. *belch* "
        elif best_value > 100:
            utterance += "Check it, I’m stackin’ up W's. This is, like, a masterclass in ownage. "
        elif best_value < -500:
            utterance += "Pffft…like your defense is as weak as a flat seltzer on Taco Tuesday. You're toast, dude. "
        else:
            utterance += "Man, the board's still kinda chill—but I’m just gettin’ warmed up, ya feel? "

        if "win" in lower_remark:
            utterance += "You talkin' about winning? Brah, that's hilarious. "

        utterance += "Victory is, like, totally mine, dude."
        return utterance.strip()

    def apply_move(self, state, move):
        """
        Returns a new state with the given move applied.
        """
        new_state = copy.deepcopy(state)
        r, c = move
        if new_state.board[r][c] != " ":
            raise ValueError(f"Invalid Move: Position ({r}, {c}) is occupied.")
        new_state.board[r][c] = state.whose_move
        new_state.whose_move = "O" if state.whose_move == "X" else "X"
        return new_state

    def get_available_moves(self, state):
        moves = []
        for r in range(len(state.board)):
            for c in range(len(state.board[0])):
                if state.board[r][c] == " ":
                    moves.append((r, c))
        return moves

    def is_terminal(self, state):
        """
        Returns True if the state is terminal (a win or a draw), otherwise False.
        """
        k = self.current_game_type.k if self.current_game_type else None
        if k is None and hasattr(state, 'k'):
            k = state.k
        if k is None:
            return False
        board = state.board
        H = len(board)
        W = len(board[0]) if H else 0
        for r in range(H):
            for c in range(W):
                if board[r][c] in ('X', 'O'):
                    if winTesterForK(state, (r, c), k) != "No win":
                        return True
        # draw if no spaces left
        for row in board:
            if ' ' in row:
                return False
        return True

    def static_eval(self, state, game_type=None):
        """
        A simple static evaluation: higher values favor X, lower favor O.
        """
        x_score = self.count_sequences(state, "X")
        o_score = self.count_sequences(state, "O")
        return x_score - o_score

    def count_sequences(self, state, player):
        count = 0
        sequences = self.get_all_possible_sequences(state, self.current_game_type.k)
        for seq in sequences:
            if seq.count(player) == self.current_game_type.k:
                count += 1000
            elif (
                seq.count(player) == self.current_game_type.k - 1
                and seq.count(" ") == 1
            ):
                count += 50
            elif (
                seq.count(player) == self.current_game_type.k - 2
                and seq.count(" ") == 2
            ):
                count += 10
        return count

    def get_all_possible_sequences(self, state, k):
        sequences = []
        board = state.board
        rows, cols = len(board), len(board[0])
        # Horizontal sequences.
        for r in range(rows):
            for c in range(cols - k + 1):
                sequences.append([board[r][c + i] for i in range(k)])
        # Vertical sequences.
        for c in range(cols):
            for r in range(rows - k + 1):
                sequences.append([board[r + i][c] for i in range(k)])
        # Diagonal (main diagonal).
        for r in range(rows - k + 1):
            for c in range(cols - k + 1):
                sequences.append([board[r + i][c + i] for i in range(k)])
        # Anti-diagonal sequences.
        for r in range(rows - k + 1):
            for c in range(k - 1, cols):
                sequences.append([board[r + i][c - i] for i in range(k)])
        return sequences
