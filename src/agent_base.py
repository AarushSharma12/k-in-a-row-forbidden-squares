"""
Base Game Agent Module

Provides the abstract base class for all game-playing agents in the
K-in-a-Row framework. Concrete implementations should inherit from
BaseGameAgent and implement the required methods.

Author: Aarush Sharma
"""

from abc import ABC, abstractmethod


class BaseGameAgent(ABC):
    """
    Abstract base class for game-playing agents.

    This class defines the interface that all game agents must implement.
    It provides basic agent identification and requires subclasses to
    implement the core game-playing logic.

    Attributes:
        side: The player side this agent represents ('X' or 'O').
        nickname: Short identifier for the agent.
        long_name: Full descriptive name of the agent.
        voice_synthesis_enabled: Whether to use text-to-speech for remarks.
    """

    def __init__(self):
        """Initialize the base game agent with default values."""
        self.side = None
        self.nickname = ""
        self.long_name = ""
        self.voice_synthesis_enabled = False

    def introduce(self) -> str:
        """
        Return a string introducing this agent.

        Returns:
            str: A brief introduction message from this agent.
        """
        return f"I am {self.long_name}, a game-playing agent."

    def set_side(self, side: str) -> None:
        """
        Set which side this agent plays.

        Args:
            side: The player identifier ('X' or 'O').
        """
        self.side = side

    def get_nickname(self) -> str:
        """
        Get the agent's short name.

        Returns:
            str: The agent's nickname.
        """
        return self.nickname

    def get_long_name(self) -> str:
        """
        Get the agent's full name.

        Returns:
            str: The agent's long descriptive name.
        """
        return self.long_name

    @abstractmethod
    def make_move(self, state, utterance_source: str = ""):
        """
        Determine and return the agent's next move.

        This method must be implemented by all concrete agent classes.
        It should analyze the current game state and return a valid move.

        Args:
            state: The current game state object.
            utterance_source: Optional string containing opponent's last remark.

        Returns:
            A tuple containing:
                - move: The chosen move as a list [row, col] or similar.
                - new_state: The resulting state after the move.
                - remark: A string comment about the move.

        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement make_move()")

    def minimax(self, state, depth_remaining: int, pruning: bool = False,
                alpha: float = float('-inf'), beta: float = float('inf')):
        """
        Execute minimax search with optional alpha-beta pruning.

        This method should be implemented by agents that use minimax-based
        decision making. The base implementation raises NotImplementedError.

        Args:
            state: The current game state to evaluate.
            depth_remaining: Maximum search depth from current position.
            pruning: Whether to use alpha-beta pruning.
            alpha: Alpha value for pruning (best value for maximizer).
            beta: Beta value for pruning (best value for minimizer).

        Returns:
            A dictionary containing search results with keys such as:
                - 'best_move': The optimal move found.
                - 'best_value': The minimax value of the best move.
                - 'nodes_expanded': Count of nodes examined.
                - 'cutoffs': Count of pruning cutoffs (if pruning enabled).

        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement minimax()")

    def static_eval(self, state) -> float:
        """
        Evaluate the given state and return a heuristic score.

        Positive values favor the maximizing player (typically 'X'),
        negative values favor the minimizing player (typically 'O').

        Args:
            state: The game state to evaluate.

        Returns:
            float: The heuristic evaluation score.

        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement static_eval()")

    def generate_remark(self, state, move, value: float) -> str:
        """
        Generate a contextual remark about the current game situation.

        Args:
            state: The current game state.
            move: The move being made.
            value: The evaluated value of the position.

        Returns:
            str: A remark string, or empty string if no remark.
        """
        return ""
