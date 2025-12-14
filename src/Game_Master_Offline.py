"""
Offline Game Engine for K-in-a-Row Variants

Handles the game loop, state management, move validation, and HTML rendering
for offline (non-server) gameplay between two agents.

Author: Aarush Sharma
"""

import time
import html

# Player constants
PLAYER_X = 'X'
PLAYER_O = 'O'

# For backward compatibility
PLAYERX = PLAYER_X
PLAYERO = PLAYER_O


class OfflineGameMaster:
    """
    Manages offline games between two agents.

    This class orchestrates turn-based gameplay, validates moves,
    tracks game state, and generates HTML output for visualization.

    Attributes:
        initial_state: The starting game state.
        player_x_agent: The agent playing as X.
        player_o_agent: The agent playing as O.
        game_history: List of states representing the game progression.
        move_history: List of moves made during the game.
        current_player: Which player's turn it is.
        game_over: Whether the game has ended.
        winner: The winning player, or None for draw/ongoing.
    """

    def __init__(self, initial_state, player_x_agent, player_o_agent,
                 win_tester=None, k=5):
        """
        Initialize the game master with agents and starting state.

        Args:
            initial_state: The initial game state object.
            player_x_agent: Agent instance for player X.
            player_o_agent: Agent instance for player O.
            win_tester: Function to check win conditions.
            k: Number in a row needed to win.
        """
        self.initial_state = initial_state
        self.player_x_agent = player_x_agent
        self.player_o_agent = player_o_agent
        self.win_tester = win_tester
        self.k = k

        self.game_history = [initial_state]
        self.move_history = []
        self.remark_history = []
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None

        # Set agent sides
        self.player_x_agent.set_side(PLAYER_X)
        self.player_o_agent.set_side(PLAYER_O)

    def get_current_agent(self):
        """
        Get the agent whose turn it is.

        Returns:
            The agent object for the current player.
        """
        if self.current_player == PLAYER_X:
            return self.player_x_agent
        return self.player_o_agent

    def get_opponent_agent(self):
        """
        Get the agent who is not currently playing.

        Returns:
            The agent object for the opponent.
        """
        if self.current_player == PLAYER_X:
            return self.player_o_agent
        return self.player_x_agent

    def switch_player(self):
        """Switch the current player to the opponent."""
        if self.current_player == PLAYER_X:
            self.current_player = PLAYER_O
        else:
            self.current_player = PLAYER_X

    def play_move(self):
        """
        Execute one move in the game.

        Gets a move from the current agent, validates it, updates state,
        checks for win/draw conditions, and switches players.

        Returns:
            dict: Information about the move including:
                - 'move': The move made.
                - 'remark': Agent's remark about the move.
                - 'time': Time taken to compute the move.
                - 'game_over': Whether game ended.
                - 'winner': Winner if game ended.
        """
        if self.game_over:
            return {'game_over': True, 'winner': self.winner}

        current_state = self.game_history[-1]
        agent = self.get_current_agent()

        # Get opponent's last remark if available
        last_remark = ""
        if self.remark_history:
            last_remark = self.remark_history[-1]

        # Time the move computation
        start_time = time.time()
        move, new_state, remark = agent.make_move(current_state, last_remark)
        elapsed_time = time.time() - start_time

        # Update histories
        self.move_history.append(move)
        self.game_history.append(new_state)
        self.remark_history.append(remark)

        # Check for win condition
        if self.win_tester:
            result = self.win_tester(new_state, move, self.k)
            if result in [PLAYER_X, PLAYER_O]:
                self.game_over = True
                self.winner = result
            elif result == 'draw':
                self.game_over = True
                self.winner = None

        # Switch to next player
        if not self.game_over:
            self.switch_player()

        return {
            'move': move,
            'remark': remark,
            'time': elapsed_time,
            'game_over': self.game_over,
            'winner': self.winner
        }

    def play_game(self, max_moves=1000, verbose=True):
        """
        Play a complete game until win, draw, or move limit.

        Args:
            max_moves: Maximum number of moves before forcing a draw.
            verbose: Whether to print move information.

        Returns:
            dict: Game result including winner and move count.
        """
        move_count = 0

        while not self.game_over and move_count < max_moves:
            result = self.play_move()
            move_count += 1

            if verbose:
                agent = self.get_opponent_agent() if not self.game_over else self.get_current_agent()
                print(f"Move {move_count}: {agent.get_nickname()} plays {result['move']}")
                if result['remark']:
                    print(f"  \"{result['remark']}\"")
                print(f"  (computed in {result['time']:.3f}s)")

        return {
            'winner': self.winner,
            'moves': move_count,
            'history': self.game_history
        }

    def generate_html_report(self) -> str:
        """
        Generate an HTML report of the game.

        Returns:
            str: Complete HTML document showing game progression.
        """
        html_parts = [
            '<!DOCTYPE html>',
            '<html><head>',
            '<title>K-in-a-Row Game Report</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; }',
            '.move { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }',
            '.remark { font-style: italic; color: #666; }',
            '.winner { font-weight: bold; color: green; font-size: 1.2em; }',
            '</style>',
            '</head><body>',
            f'<h1>Game: {self.player_x_agent.get_long_name()} vs {self.player_o_agent.get_long_name()}</h1>'
        ]

        for i, move in enumerate(self.move_history):
            player = PLAYER_X if i % 2 == 0 else PLAYER_O
            agent = self.player_x_agent if player == PLAYER_X else self.player_o_agent
            remark = self.remark_history[i] if i < len(self.remark_history) else ""

            html_parts.append(f'<div class="move">')
            html_parts.append(f'<strong>Move {i + 1}:</strong> {html.escape(agent.get_nickname())} ({player}) plays {move}')
            if remark:
                html_parts.append(f'<div class="remark">"{html.escape(remark)}"</div>')
            html_parts.append('</div>')

        # Game result
        if self.game_over:
            if self.winner:
                winner_agent = self.player_x_agent if self.winner == PLAYER_X else self.player_o_agent
                html_parts.append(f'<p class="winner">Winner: {html.escape(winner_agent.get_long_name())} ({self.winner})</p>')
            else:
                html_parts.append('<p class="winner">Result: Draw</p>')

        html_parts.extend(['</body></html>'])
        return '\n'.join(html_parts)


def run_game(initial_state, player_x, player_o, win_tester=None, k=5, verbose=True):
    """
    Convenience function to run a complete game.

    Args:
        initial_state: Starting game state.
        player_x: Agent for player X.
        player_o: Agent for player O.
        win_tester: Win condition checker function.
        k: Number in a row to win.
        verbose: Print move information.

    Returns:
        dict: Game results.
    """
    gm = OfflineGameMaster(initial_state, player_x, player_o, win_tester, k)
    return gm.play_game(verbose=verbose)
