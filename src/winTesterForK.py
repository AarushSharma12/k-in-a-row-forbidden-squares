"""
Win Condition Checker for K-in-a-Row Games

Provides functions to determine if a player has won by achieving
K consecutive pieces in any direction (horizontal, vertical, diagonal).

Author: Aarush Sharma
"""


def check_win_condition(state, move, k):
    """
    Check if the last move resulted in a win condition.

    Examines the board state to determine if the player who made the
    last move has achieved K consecutive pieces in any direction:
    horizontal, vertical, or either diagonal.

    Args:
        state: The current game state object. Must have a 'board' attribute
               that is a 2D list, where each cell contains 'X', 'O', or ' '.
        move: The last move made, as a list or tuple [row, col].
        k: The number of consecutive pieces required to win.

    Returns:
        str or None: 
            - 'X' if player X has won
            - 'O' if player O has won  
            - 'draw' if the board is full with no winner
            - None if the game should continue

    Example:
        >>> state = GameState(board=[['X','X','X'], [' ','O','O'], [' ',' ',' ']])
        >>> check_win_condition(state, [0, 2], 3)
        'X'
    """
    board = state.board
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    if move is None:
        return _check_full_board(board, k)

    row, col = move[0], move[1]
    player = board[row][col]

    if player not in ['X', 'O']:
        return None

    # Check all four directions from the last move
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal (top-left to bottom-right)
        (1, -1),  # Anti-diagonal (top-right to bottom-left)
    ]

    for delta_row, delta_col in directions:
        count = 1  # Count the piece at the move position

        # Count in positive direction
        count += _count_in_direction(board, row, col, delta_row, delta_col, player, rows, cols)

        # Count in negative direction
        count += _count_in_direction(board, row, col, -delta_row, -delta_col, player, rows, cols)

        if count >= k:
            return player

    # Check for draw (board full)
    if _is_board_full(board):
        return 'draw'

    return None


def _count_in_direction(board, start_row, start_col, delta_row, delta_col, player, rows, cols):
    """
    Count consecutive pieces in a single direction.

    Args:
        board: The game board (2D list).
        start_row: Starting row position.
        start_col: Starting column position.
        delta_row: Row direction increment (-1, 0, or 1).
        delta_col: Column direction increment (-1, 0, or 1).
        player: The player piece to count ('X' or 'O').
        rows: Total number of rows.
        cols: Total number of columns.

    Returns:
        int: Number of consecutive matching pieces (not including start).
    """
    count = 0
    current_row = start_row + delta_row
    current_col = start_col + delta_col

    while (0 <= current_row < rows and 
           0 <= current_col < cols and 
           board[current_row][current_col] == player):
        count += 1
        current_row += delta_row
        current_col += delta_col

    return count


def _is_board_full(board):
    """
    Check if all board positions are occupied.

    Args:
        board: The game board (2D list).

    Returns:
        bool: True if no empty spaces remain.
    """
    for row in board:
        for cell in row:
            if cell == ' ' or cell == '-':
                return False
    return True


def _check_full_board(board, k):
    """
    Scan entire board for win condition (used when no specific move given).

    Args:
        board: The game board (2D list).
        k: Number in a row needed to win.

    Returns:
        str or None: 'X', 'O', 'draw', or None.
    """
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    for player in ['X', 'O']:
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == player:
                    # Check horizontal
                    if col + k <= cols:
                        if all(board[row][col + i] == player for i in range(k)):
                            return player

                    # Check vertical
                    if row + k <= rows:
                        if all(board[row + i][col] == player for i in range(k)):
                            return player

                    # Check diagonal
                    if row + k <= rows and col + k <= cols:
                        if all(board[row + i][col + i] == player for i in range(k)):
                            return player

                    # Check anti-diagonal
                    if row + k <= rows and col - k + 1 >= 0:
                        if all(board[row + i][col - i] == player for i in range(k)):
                            return player

    if _is_board_full(board):
        return 'draw'

    return None


# Backward compatibility alias
winTesterForK = check_win_condition

