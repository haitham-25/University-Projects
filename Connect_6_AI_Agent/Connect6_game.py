import tkinter as tk
import math
import time
import copy
import random
import tkinter.messagebox
import logging
import pickle
import os
import pygame

# --- Constants ---

# Board dimensions
BOARD_SIZE = 19

# Number of consecutive stones required to win
WIN_SEQUENCE = 6

# Player values
EMPTY = 0
PLAYER_1 = 1  # Human player
PLAYER_2 = 2  # AI player

# GUI drawing parameters
CELL_SIZE = 30
BOARD_PADDING = 20
STONE_RADIUS = CELL_SIZE // 2 - 2

# AI types
AI_MINIMAX_ONLY = "Minimax Only"
AI_MINIMAX_ALPHA_BETA = "Minimax + Alpha-Beta"
AI_HEURISTIC_BLOCK_THREATS = "Heuristic Block Threats "#(Limited Search)
AI_MINIMAX_WITH_THREATS = "Minimax + Threat Heuristic"
AI_HEURISTIC_OPEN_THREE = "Heuristic Open Three "#(Limited Search)
AI_MINIMAX_WITH_OPEN_THREE = "Minimax + Open Three Heuristic"
AI_HEURISTIC_REDUCTION = "Heuristic Reduction"
AI_SYMMETRY_REDUCTION = "Symmetry Reduction"

# Default AI depth
DEFAULT_AI_DEPTH = 2
MAX_AI_DEPTH = 4

# Radius for heuristic reduction
REDUCTION_RADIUS = 3

# Save file
SAVE_FILE = "connect6_save.pkl"

# Logging setup
logging.basicConfig(filename='ai_moves.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# --- Board Class ---

class Board:
    def __init__(self, size=BOARD_SIZE):
        """Initialize a board of given size with empty intersections."""
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]

    def is_valid_move(self, row, col):
        """Check if a move at (row, col) is valid."""
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == EMPTY

    def make_move(self, row, col, player):
        """Place a player's stone at (row, col) if valid."""
        if self.is_valid_move(row, col):
            self.board[row][col] = player
            return True
        return False

    def check_win(self, row, col, player):
        """Check if placing a stone at (row, col) results in a win for player. Return (win, winning_line)."""
        if self.board[row][col] != player:
            return False, None
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            winning_line = [(row, col)]
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                winning_line.append((r, c))
                r, c = r + dr, c + dc
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                winning_line.insert(0, (r, c))
                r, c = r - dr, c - dc
            if count >= WIN_SEQUENCE:
                return True, winning_line
        return False, None

    def is_board_full(self):
        """Check if the board has no empty intersections."""
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == EMPTY:
                    return False
        return True

    def get_empty_intersections(self):
        """Return a list of all empty (row, col) intersections."""
        empty_spots = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == EMPTY:
                    empty_spots.append((r, c))
        return empty_spots

    def copy(self):
        """Return a deep copy of the board."""
        new_board = Board(self.size)
        new_board.board = copy.deepcopy(self.board)
        return new_board

    def __str__(self):
        """Return a string representation of the board."""
        s = ""
        for r in range(self.size):
            s += " ".join([str(x) for x in self.board[r]]) + "\n"
        return s


# --- AI Strategies and Functions ---

def has_winning_move(board, player):
    """Check if the specified player has an immediate winning move."""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(board.size):
        for c in range(board.size):
            for dr, dc in directions:
                for offset in range(-WIN_SEQUENCE + 1, 1):
                    start_r, start_c = r + offset * dr, c + offset * dc
                    if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                        continue
                    count = 0
                    empty_spot = None
                    for i in range(WIN_SEQUENCE):
                        curr_r, curr_c = start_r + i * dr, start_c + i * dc
                        if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                            break
                        if board.board[curr_r][curr_c] == player:
                            count += 1
                        elif board.board[curr_r][curr_c] == EMPTY and (i == 0 or i == WIN_SEQUENCE - 1):
                            empty_spot = (curr_r, curr_c)
                    if count == WIN_SEQUENCE - 1 and empty_spot:
                        return True
    return False


def find_critical_threats(board, player):
    """Find immediate threats where opponent could win in next move"""
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2
    threats = []
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(board.size):
        for c in range(board.size):
            for dr, dc in directions:
                for offset in range(-WIN_SEQUENCE + 1, 1):
                    start_r, start_c = r + offset * dr, c + offset * dc
                    if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                        continue
                    count = 0
                    empty_spot = None
                    for i in range(WIN_SEQUENCE):
                        curr_r, curr_c = start_r + i * dr, start_c + i * dc
                        if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                            break
                        if board.board[curr_r][curr_c] == opponent:
                            count += 1
                        elif board.board[curr_r][curr_c] == EMPTY and (i == 0 or i == WIN_SEQUENCE - 1):
                            empty_spot = (curr_r, curr_c)
                    if count == WIN_SEQUENCE - 1 and empty_spot:
                        threats.append(empty_spot)
    return threats


def evaluate(board, player):
    """
    Evaluate the board state for the given player with improved defensive weights.
    """
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2
    score = 0

    # Adjusted weights with higher penalties for opponent threats
    player_weights = {1: 1, 2: 10, 3: 100, 4: 5000, 5: 1000000, 6: 10000000}
    opponent_weights = {1: 1, 2: 20, 3: 500, 4: 20000, 5: 50000000, 6: 10000000}

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(board.size):
        for c in range(board.size):
            if board.board[r][c] == EMPTY:
                continue
            current_player = board.board[r][c]
            current_opponent = PLAYER_1 if current_player == PLAYER_2 else PLAYER_2

            for dr, dc in directions:
                for offset in range(WIN_SEQUENCE):
                    start_r, start_c = r - offset * dr, c - offset * dc
                    if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                        continue

                    player_stones = 0
                    opponent_stones = 0
                    line = []

                    for i in range(WIN_SEQUENCE):
                        curr_r, curr_c = start_r + i * dr, start_c + i * dc
                        if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                            break
                        cell_value = board.board[curr_r][curr_c]
                        line.append(cell_value)
                        if cell_value == current_player:
                            player_stones += 1
                        elif cell_value == current_opponent:
                            opponent_stones += 1

                    if len(line) == WIN_SEQUENCE:
                        if opponent_stones == 0:
                            # Player sequence found
                            if player_stones == WIN_SEQUENCE:
                                if current_player == player:
                                    return 10000000  # Immediate win
                                else:
                                    return -10000000  # Immediate loss

                            if player_stones in player_weights:
                                is_open_start = False
                                if 0 <= start_r - dr < board.size and 0 <= start_c - dc < board.size:
                                    if board.board[start_r - dr][start_c - dc] == EMPTY:
                                        is_open_start = True

                                is_open_end = False
                                end_r, end_c = start_r + WIN_SEQUENCE * dr, start_c + WIN_SEQUENCE * dc
                                if 0 <= end_r < board.size and 0 <= end_c < board.size:
                                    if board.board[end_r][end_c] == EMPTY:
                                        is_open_end = True

                                line_score = player_weights[player_stones] if current_player == player else - \
                                opponent_weights[player_stones]

                                if is_open_start and is_open_end:
                                    line_score *= 2
                                elif is_open_start or is_open_end:
                                    line_score *= 1.5

                                score += line_score
    return score


def threat_focused_heuristic(board, player):
    """
    Heuristic that prioritizes blocking opponent threats and creating own threats.
    """
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2

    # First check for immediate wins/losses
    if has_winning_move(board, player):
        return 10000000
    if has_winning_move(board, opponent):
        return -10000000

    score = 0
    weights = {1: 1, 2: 10, 3: 1000, 4: 10000, 5: 150000, 6: 10000000}
    opponent_weights = {1: 1, 2: 20, 3: 1500, 4: 30000, 5: 200000, 6: 10000000}
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(board.size):
        for c in range(board.size):
            if board.board[r][c] == EMPTY:
                continue
            current_player = board.board[r][c]
            current_opponent = PLAYER_1 if current_player == PLAYER_2 else PLAYER_2

            for dr, dc in directions:
                for offset in range(WIN_SEQUENCE):
                    start_r = r - offset * dr
                    start_c = c - offset * dc

                    if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                        continue

                    player_stones = 0
                    opponent_stones = 0
                    line = []

                    for i in range(WIN_SEQUENCE):
                        curr_r = start_r + i * dr
                        curr_c = start_c + i * dc
                        if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                            break
                        cell = board.board[curr_r][curr_c]
                        line.append(cell)
                        if cell == current_player:
                            player_stones += 1
                        elif cell == current_opponent:
                            opponent_stones += 1

                    if len(line) == WIN_SEQUENCE:
                        if opponent_stones == 0:
                            if player_stones == WIN_SEQUENCE:
                                return 10000000 if current_player == player else -10000000

                            if player_stones in weights:
                                is_open_start = False
                                if 0 <= start_r - dr < board.size and 0 <= start_c - dc < board.size:
                                    if board.board[start_r - dr][start_c - dc] == EMPTY:
                                        is_open_start = True

                                is_open_end = False
                                end_r = start_r + WIN_SEQUENCE * dr
                                end_c = start_c + WIN_SEQUENCE * dc
                                if 0 <= end_r < board.size and 0 <= end_c < board.size:
                                    if board.board[end_r][end_c] == EMPTY:
                                        is_open_end = True

                                line_score = weights[player_stones] if current_player == player else -opponent_weights[
                                    player_stones]
                                if is_open_start and is_open_end:
                                    line_score *= 4
                                elif is_open_start or is_open_end:
                                    line_score *= 2

                                score += line_score
    return score


def heuristic_open_three(board, player):
    """
    Heuristic that evaluates open three sequences with improved defensive awareness.
    """
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2

    # Check for immediate threats first
    threats = find_critical_threats(board, player)
    if threats:
        return -9000000  # Very high penalty for allowing opponent threats

    score = 0
    weights = {1: 1, 2: 10, 3: 1000, 4: 5000, 5: 30000000, 6: 10000000}
    opponent_weights = {1: 1, 2: 15, 3: 1500, 4: 10000, 5: 50000000, 6: 10000000}
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(board.size):
        for c in range(board.size):
            if board.board[r][c] == EMPTY:
                continue
            current_player = board.board[r][c]
            current_opponent = PLAYER_1 if current_player == PLAYER_2 else PLAYER_2
            for dr, dc in directions:
                for offset in range(WIN_SEQUENCE):
                    start_r, start_c = r - offset * dr, c - offset * dc
                    if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                        continue
                    player_stones = 0
                    opponent_stones = 0
                    line = []
                    for i in range(WIN_SEQUENCE):
                        curr_r, curr_c = start_r + i * dr, start_c + i * dc
                        if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                            break
                        cell_value = board.board[curr_r][curr_c]
                        line.append(cell_value)
                        if cell_value == current_player:
                            player_stones += 1
                        elif cell_value == current_opponent:
                            opponent_stones += 1
                    if len(line) == WIN_SEQUENCE:
                        if opponent_stones == 0:
                            if player_stones == WIN_SEQUENCE:
                                if current_player == player:
                                    return 10000000
                                else:
                                    return -10000000
                            if player_stones in weights:
                                is_open_start = False
                                if 0 <= start_r - dr < board.size and 0 <= start_c - dc < board.size:
                                    if board.board[start_r - dr][start_c - dc] == EMPTY:
                                        is_open_start = True
                                is_open_end = False
                                end_r, end_c = start_r + WIN_SEQUENCE * dr, start_c + WIN_SEQUENCE * dc
                                if 0 <= end_r < board.size and 0 <= end_c < board.size:
                                    if board.board[end_r][end_c] == EMPTY:
                                        is_open_end = True
                                line_score = weights[player_stones] if current_player == player else -opponent_weights[
                                    player_stones]
                                if is_open_start and is_open_end:
                                    if player_stones == 3:
                                        line_score *= 5
                                    else:
                                        line_score *= 2
                                elif is_open_start or is_open_end:
                                    if player_stones == 3:
                                        line_score *= 3
                                    else:
                                        line_score *= 1.5
                                score += line_score
    return score


def alphabeta(board, depth, alpha, beta, is_maximizing_player, heuristic_func, get_moves_func, original_player):
    """
    Implement alpha-beta pruning with improved threat detection.
    """
    if depth == 0 or board.is_board_full():
        return heuristic_func(board, original_player), None

    # Check for immediate threats at the start of each node evaluation
    if is_maximizing_player:
        threats = find_critical_threats(board, original_player)
        if threats:
            # If we're maximizing and find opponent threats, prioritize blocking
            blocking_move = threats[0]
            empty_spots = board.get_empty_intersections()
            empty_spots.remove(blocking_move)
            if empty_spots:
                second_move = random.choice(empty_spots)
                return float('inf'), (blocking_move, second_move)

    possible_moves_pairs = get_moves_func(board)
    if not possible_moves_pairs:
        return heuristic_func(board, original_player), None

    def score_move_pair(move1, move2):
        temp_board = board.copy()
        temp_board.make_move(move1[0], move1[1], original_player if is_maximizing_player else (
            PLAYER_1 if original_player == PLAYER_2 else PLAYER_2))
        temp_board.make_move(move2[0], move2[1], original_player if is_maximizing_player else (
            PLAYER_1 if original_player == PLAYER_2 else PLAYER_2))
        return heuristic_func(temp_board, original_player)

    possible_moves_pairs.sort(key=lambda p: score_move_pair(p[0], p[1]), reverse=is_maximizing_player)
    best_move_pair = None

    if is_maximizing_player:
        max_eval = -math.inf
        current_player = original_player
        for move1, move2 in possible_moves_pairs:
            temp_board1 = board.copy()
            if not temp_board1.make_move(move1[0], move1[1], current_player):
                continue
            if temp_board1.check_win(move1[0], move1[1], current_player)[0]:
                eval = 10000000
            else:
                temp_board2 = temp_board1.copy()
                if not temp_board2.is_valid_move(move2[0], move2[1]):
                    continue
                if not temp_board2.make_move(move2[0], move2[1], current_player):
                    continue
                if temp_board2.check_win(move2[0], move2[1], current_player)[0]:
                    eval = 10000000
                else:
                    eval, _ = alphabeta(temp_board2, depth - 1, alpha, beta, False, heuristic_func, get_moves_func,
                                        original_player)
            if eval > max_eval:
                max_eval = eval
                best_move_pair = (move1, move2)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move_pair
    else:
        min_eval = math.inf
        current_player = PLAYER_1 if original_player == PLAYER_2 else PLAYER_2
        for move1, move2 in possible_moves_pairs:
            temp_board1 = board.copy()
            if not temp_board1.make_move(move1[0], move1[1], current_player):
                continue
            if temp_board1.check_win(move1[0], move1[1], current_player)[0]:
                eval = -10000000
            else:
                temp_board2 = temp_board1.copy()
                if not temp_board2.is_valid_move(move2[0], move2[1]):
                    continue
                if not temp_board2.make_move(move2[0], move2[1], current_player):
                    continue
                if temp_board2.check_win(move2[0], move2[1], current_player)[0]:
                    eval = -10000000
                else:
                    eval, _ = alphabeta(temp_board2, depth - 1, alpha, beta, True, heuristic_func, get_moves_func,
                                        original_player)
            if eval < min_eval:
                min_eval = eval
                best_move_pair = (move1, move2)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move_pair


# --- Move Generation Functions ---

def get_all_possible_pairs(board):
    """Generate all possible pairs of empty intersections on the board."""
    empty_spots = board.get_empty_intersections()
    possible_pairs = []
    for i in range(len(empty_spots)):
        for j in range(i + 1, len(empty_spots)):
            possible_pairs.append((empty_spots[i], empty_spots[j]))
    return possible_pairs


def get_reduced_moves_pairs(board):
    """
    Generate move pairs from empty intersections near occupied spots,
    reducing the search space but including critical threats.
    """
    empty_spots = board.get_empty_intersections()
    occupied_spots = [(r, c) for r in range(board.size) for c in range(board.size) if board.board[r][c] != EMPTY]

    # Always include spots that are part of critical threats
    critical_threats = find_critical_threats(board, PLAYER_2)
    nearby_empty_spots = set(critical_threats)

    for er, ec in empty_spots:
        for or_, oc in occupied_spots:
            distance = abs(er - or_) + abs(ec - oc)
            if distance <= REDUCTION_RADIUS:
                nearby_empty_spots.add((er, ec))
                break

    if not occupied_spots:
        center = board.size // 2
        for r in range(max(0, center - REDUCTION_RADIUS), min(board.size, center + REDUCTION_RADIUS + 1)):
            for c in range(max(0, center - REDUCTION_RADIUS), min(board.size, center + REDUCTION_RADIUS + 1)):
                if board.board[r][c] == EMPTY:
                    nearby_empty_spots.add((r, c))

    nearby_empty_list = list(nearby_empty_spots)
    possible_pairs = []
    for i in range(len(nearby_empty_list)):
        for j in range(i + 1, len(nearby_empty_list)):
            possible_pairs.append((nearby_empty_list[i], nearby_empty_list[j]))
    return possible_pairs


def get_symmetry_reduced_pairs(board, heuristic_func=evaluate, player=PLAYER_2):
    """
    Generate move pairs considering board symmetries, with priority to threat blocks.
    """
    # Check for immediate threats first
    threats = find_critical_threats(board, player)
    if threats:
        blocking_move = threats[0]
        empty_spots = board.get_empty_intersections()
        empty_spots.remove(blocking_move)
        if empty_spots:
            second_move = random.choice(empty_spots)
            return [(blocking_move, second_move)]

    # Proceed with symmetry reduction if no immediate threats
    empty_spots = board.get_empty_intersections()
    occupied_spots = [(r, c) for r in range(board.size) for c in range(board.size) if board.board[r][c] != EMPTY]
    nearby_empty_spots = set()

    for er, ec in empty_spots:
        for or_, oc in occupied_spots:
            if abs(er - or_) + abs(ec - oc) <= REDUCTION_RADIUS:
                nearby_empty_spots.add((er, ec))
                break

    if not occupied_spots:
        center = board.size // 2
        for r in range(max(0, center - REDUCTION_RADIUS), min(board.size, center + REDUCTION_RADIUS + 1)):
            for c in range(max(0, center - REDUCTION_RADIUS), min(board.size, center + REDUCTION_RADIUS + 1)):
                if board.board[r][c] == EMPTY:
                    nearby_empty_spots.add((r, c))

    empty_spots = list(nearby_empty_spots)
    symmetry_groups = {}

    for i in range(len(empty_spots)):
        for j in range(i + 1, len(empty_spots)):
            move1, move2 = empty_spots[i], empty_spots[j]
            symmetric_pairs = [
                ((move1[0], move1[1]), (move2[0], move2[1])),  # Original
                ((move1[1], board.size - 1 - move1[0]), (move2[1], board.size - 1 - move2[0])),  # 90° rotation
                ((board.size - 1 - move1[0], board.size - 1 - move1[1]),
                 (board.size - 1 - move2[0], board.size - 1 - move2[1])),  # 180° rotation
                ((board.size - 1 - move1[1], move1[0]), (board.size - 1 - move2[1], move2[0])),  # 270° rotation
                ((move1[0], board.size - 1 - move1[1]), (move2[0], board.size - 1 - move2[1])),  # Horizontal reflection
                ((board.size - 1 - move1[0], move1[1]), (board.size - 1 - move2[0], move2[1])),  # Vertical reflection
                ((move1[1], move1[0]), (move2[1], move2[0])),  # Main diagonal reflection
                ((board.size - 1 - move1[1], board.size - 1 - move1[0]),
                 (board.size - 1 - move2[1], board.size - 1 - move2[0]))  # Anti-diagonal reflection
            ]
            valid_pairs = [
                (p1, p2) for p1, p2 in symmetric_pairs
                if (0 <= p1[0] < board.size and 0 <= p1[1] < board.size and
                    0 <= p2[0] < board.size and 0 <= p2[1] < board.size and
                    board.board[p1[0]][p1[1]] == EMPTY and board.board[p2[0]][p2[1]] == EMPTY)
            ]
            if not valid_pairs:
                continue

            best_pair = None
            best_score = -float('inf')
            for p1, p2 in valid_pairs:
                temp_board = board.copy()
                temp_board.make_move(p1[0], p1[1], player)
                temp_board.make_move(p2[0], p2[1], player)
                if temp_board.check_win(p1[0], p1[1], player)[0] or temp_board.check_win(p2[0], p2[1], player)[0]:
                    return [(p1, p2)]  # Immediate win found
                score = heuristic_func(temp_board, player)
                if score > best_score:
                    best_score = score
                    best_pair = (p1, p2)

            if best_pair:
                canonical_pair = (
                    (min(best_pair[0][0], best_pair[1][0]), min(best_pair[0][1], best_pair[1][1])),
                    (max(best_pair[0][0], best_pair[1][0]), max(best_pair[0][1], best_pair[1][1]))
                )  # Added missing parenthesis
                symmetry_groups[canonical_pair] = (move1, move2)

    return list(symmetry_groups.values())
# --- AI Selection and Execution ---

AI_CONFIGS = {
    AI_MINIMAX_ONLY: {
        "heuristic": evaluate,
        "moves_func": get_all_possible_pairs,
        "depth": lambda x: x
    },
    AI_MINIMAX_ALPHA_BETA: {
        "heuristic": evaluate,
        "moves_func": get_all_possible_pairs,
        "depth": lambda x: x
    },
    AI_HEURISTIC_BLOCK_THREATS: {
        "heuristic": threat_focused_heuristic,
        "moves_func": get_reduced_moves_pairs,
        "depth": lambda x: min(x, 2)
    },
    AI_MINIMAX_WITH_THREATS: {
        "heuristic": threat_focused_heuristic,
        "moves_func": get_reduced_moves_pairs,
        "depth": lambda x: x
    },
    AI_HEURISTIC_OPEN_THREE: {
        "heuristic": heuristic_open_three,
        "moves_func": get_reduced_moves_pairs,
        "depth": lambda x: min(x, 2)
    },
    AI_MINIMAX_WITH_OPEN_THREE: {
        "heuristic": heuristic_open_three,
        "moves_func": get_reduced_moves_pairs,
        "depth": lambda x: x
    },
    AI_HEURISTIC_REDUCTION: {
        "heuristic": evaluate,
        "moves_func": get_reduced_moves_pairs,
        "depth": lambda x: x
    },
    AI_SYMMETRY_REDUCTION: {
        "heuristic": evaluate,
        "moves_func": lambda b: get_symmetry_reduced_pairs(b, evaluate, PLAYER_2),
        "depth": lambda x: x
    }
}


def select_ai_move(board, ai_type, max_depth):
    """
    Select the best move pair for the AI with improved defensive play.
    """
    start_time = time.perf_counter()
    config = AI_CONFIGS.get(ai_type, AI_CONFIGS[AI_MINIMAX_ALPHA_BETA])

    # First check if AI can win immediately
    def find_immediate_wins():
        winning_pairs = []
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        empty_spots = board.get_empty_intersections()

        # Single-move wins
        for r in range(board.size):
            for c in range(board.size):
                for dr, dc in directions:
                    for offset in range(-WIN_SEQUENCE + 1, 1):
                        start_r, start_c = r + offset * dr, c + offset * dc
                        if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                            continue
                        count = 0
                        empty_spot = None
                        for i in range(WIN_SEQUENCE):
                            curr_r, curr_c = start_r + i * dr, start_c + i * dc
                            if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                                break
                            if board.board[curr_r][curr_c] == PLAYER_2:
                                count += 1
                            elif board.board[curr_r][curr_c] == EMPTY and (i == 0 or i == WIN_SEQUENCE - 1):
                                empty_spot = (curr_r, curr_c)
                        if count == WIN_SEQUENCE - 1 and empty_spot and empty_spot in empty_spots:
                            temp_board = board.copy()
                            temp_board.make_move(empty_spot[0], empty_spot[1], PLAYER_2)
                            if temp_board.check_win(empty_spot[0], empty_spot[1], PLAYER_2)[0]:
                                second_spots = [s for s in empty_spots if s != empty_spot]
                                if second_spots:
                                    second_move = random.choice(second_spots)
                                    winning_pairs.append((empty_spot, second_move))
                                    logging.info(f"Single-move win found at {empty_spot}, second move {second_move}")

        # Two-move wins
        for r in range(board.size):
            for c in range(board.size):
                for dr, dc in directions:
                    for offset in range(-WIN_SEQUENCE + 1, 2):
                        start_r, start_c = r + offset * dr, c + offset * dc
                        if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                            continue
                        count = 0
                        empty_spots_in_line = []
                        for i in range(WIN_SEQUENCE):
                            curr_r, curr_c = start_r + i * dr, start_c + i * dc
                            if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                                break
                            if board.board[curr_r][curr_c] == PLAYER_2:
                                count += 1
                            elif board.board[curr_r][curr_c] == EMPTY:
                                empty_spots_in_line.append((curr_r, curr_c))
                        if count == WIN_SEQUENCE - 2 and len(empty_spots_in_line) == 2:
                            move1, move2 = empty_spots_in_line
                            if move1 in empty_spots and move2 in empty_spots:
                                temp_board = board.copy()
                                temp_board.make_move(move1[0], move1[1], PLAYER_2)
                                temp_board.make_move(move2[0], move2[1], PLAYER_2)
                                if (temp_board.check_win(move1[0], move1[1], PLAYER_2)[0] or
                                        temp_board.check_win(move2[0], move2[1], PLAYER_2)[0]):
                                    winning_pairs.append((move1, move2))
                                    logging.info(f"Two-move win found at {move1}, {move2}")

        return winning_pairs

    # Check for critical threats that must be blocked
    def find_critical_blocks():
        blocks = []
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        empty_spots = board.get_empty_intersections()

        for r in range(board.size):
            for c in range(board.size):
                for dr, dc in directions:
                    for offset in range(-WIN_SEQUENCE + 1, 1):
                        start_r, start_c = r + offset * dr, c + offset * dc
                        if not (0 <= start_r < board.size and 0 <= start_c < board.size):
                            continue
                        count = 0
                        empty_spot = None
                        for i in range(WIN_SEQUENCE):
                            curr_r, curr_c = start_r + i * dr, start_c + i * dc
                            if not (0 <= curr_r < board.size and 0 <= curr_c < board.size):
                                break
                            if board.board[curr_r][curr_c] == PLAYER_1:
                                count += 1
                            elif board.board[curr_r][curr_c] == EMPTY and (i == 0 or i == WIN_SEQUENCE - 1):
                                empty_spot = (curr_r, curr_c)
                        if count == WIN_SEQUENCE - 1 and empty_spot and empty_spot in empty_spots:
                            temp_board = board.copy()
                            temp_board.make_move(empty_spot[0], empty_spot[1], PLAYER_1)
                            if temp_board.check_win(empty_spot[0], empty_spot[1], PLAYER_1)[0]:
                                blocks.append(empty_spot)
                                logging.info(f"Critical block needed at {empty_spot}")

        return blocks

    # Use immediate win if found
    immediate_wins = find_immediate_wins()
    if immediate_wins:
        selected_pair = random.choice(immediate_wins)
        end_time = time.perf_counter()
        return selected_pair, end_time - start_time

    # Block critical threats first
    critical_blocks = find_critical_blocks()
    if critical_blocks:
        blocking_move = critical_blocks[0]
        empty_spots = board.get_empty_intersections()
        empty_spots.remove(blocking_move)
        if empty_spots:
            second_move = random.choice(empty_spots)
            end_time = time.perf_counter()
            logging.info(f"Blocking critical threat at {blocking_move} with second move at {second_move}")
            return (blocking_move, second_move), end_time - start_time

    # Otherwise, use the configured AI strategy
    best_score, best_move_pair = alphabeta(
        board.copy(),
        config["depth"](max_depth),
        -math.inf,
        math.inf,
        True,
        config["heuristic"],
        config["moves_func"],
        PLAYER_2
    )

    end_time = time.perf_counter()
    time_taken = end_time - start_time
    logging.info(f"AI Type: {ai_type}, Depth: {max_depth}, Score: {best_score}, Move Pair: {best_move_pair}")

    if best_move_pair is None:
        empty_spots = board.get_empty_intersections()
        if len(empty_spots) >= 2:
            best_score = -float('inf')
            for i in range(len(empty_spots)):
                for j in range(i + 1, len(empty_spots)):
                    move1, move2 = empty_spots[i], empty_spots[j]
                    temp_board = board.copy()
                    temp_board.make_move(move1[0], move1[1], PLAYER_2)
                    temp_board.make_move(move2[0], move2[1], PLAYER_2)
                    score = config["heuristic"](temp_board, PLAYER_2)
                    if score > best_score:
                        best_score = score
                        best_move_pair = (move1, move2)
            print("Warning: AI failed to find a move pair; using heuristic-based fallback.")
            logging.warning("AI failed to find a move pair; using heuristic-based fallback.")
        else:
            print("Error: Not enough empty spots for AI to make two moves.")
            logging.error("Not enough empty spots for AI to make two moves.")
            return None, time_taken

    return best_move_pair, time_taken


# --- GUI Class ---

class GameGUI:
    def __init__(self, root, game_manager):
        """Initialize the GUI with a root window and game manager."""
        self.root = root
        self.game_manager = game_manager
        self.canvas = None
        self.status_label = None
        self.timer_label = None
        self.menu_frame = None
        self.game_frame = None
        self.undo_button = None
        self.save_button = None
        self.load_button = None
        self.ai_option_var = tk.StringVar(value=AI_MINIMAX_ALPHA_BETA)
        self.ai_depth_var = tk.StringVar(value=str(DEFAULT_AI_DEPTH))
        self.ai_options = [
            AI_MINIMAX_ONLY,
            AI_MINIMAX_ALPHA_BETA,
            AI_HEURISTIC_BLOCK_THREATS,
            AI_MINIMAX_WITH_THREATS,
            AI_HEURISTIC_OPEN_THREE,
            AI_MINIMAX_WITH_OPEN_THREE,
            AI_HEURISTIC_REDUCTION,
            AI_SYMMETRY_REDUCTION
        ]
        self.create_widgets()

    def create_widgets(self):
        """Create and pack GUI widgets for the menu and game frames."""
        self.menu_frame = tk.Frame(self.root)
        tk.Label(self.menu_frame, text="Select AI Strategy:", font=('Arial', 14, 'bold')).pack(pady=15)
        for option in self.ai_options:
            tk.Radiobutton(self.menu_frame, text=option, variable=self.ai_option_var, value=option,
                           font=('Arial', 12)).pack(anchor='w', padx=20)
        tk.Label(self.menu_frame, text="AI Search Depth (1–4, >2 is slow on 19x19):", font=('Arial', 14, 'bold')).pack(
            pady=15)
        tk.Entry(self.menu_frame, textvariable=self.ai_depth_var, width=5, font=('Arial', 12)).pack(pady=5)
        tk.Button(self.menu_frame, text="Start Game", command=self.start_game_from_menu, font=('Arial', 14, 'bold'),
                  bg='green', fg='white').pack(pady=10)
        tk.Button(self.menu_frame, text="Load Saved Game", command=self.game_manager.load_game,
                  font=('Arial', 14, 'bold'), bg='blue', fg='white').pack(pady=10)
        self.game_frame = tk.Frame(self.root)
        canvas_size = (BOARD_SIZE - 1) * CELL_SIZE + 2 * BOARD_PADDING
        self.canvas = tk.Canvas(self.game_frame, width=canvas_size, height=canvas_size, bg='burlywood')
        self.canvas.pack(pady=BOARD_PADDING)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.status_label = tk.Label(self.game_frame, text="Game started. Player 1's turn.", font=('Arial', 14))
        self.status_label.pack(pady=5)
        self.timer_label = tk.Label(self.game_frame, text="AI time: 0.000000 seconds", font=('Arial', 12))
        self.timer_label.pack(pady=5)
        self.undo_button = tk.Button(self.game_frame, text="Undo", command=self.game_manager.undo_move,
                                     font=('Arial', 12), bg='orange', fg='white', state='disabled')
        self.undo_button.pack(pady=5)
        self.save_button = tk.Button(self.game_frame, text="Save Game", command=self.game_manager.save_game,
                                     font=('Arial', 12), bg='purple', fg='white')
        self.save_button.pack(pady=5)
        self.load_button = tk.Button(self.game_frame, text="Load Game", command=self.game_manager.load_game,
                                     font=('Arial', 12), bg='blue', fg='white')
        self.load_button.pack(pady=5)
        self.menu_button = tk.Button(self.game_frame, text="Main Menu", command=self.show_main_menu, font=('Arial', 12),
                                     bg='gray', fg='white')

    def show_main_menu(self):
        """Show the main menu and hide the game frame."""
        if self.game_frame:
            self.game_frame.pack_forget()
        if self.menu_button:
            self.menu_button.pack_forget()
        self.menu_frame.pack(expand=True, fill='both')

    def start_game_from_menu(self):
        """Start a new game with the selected AI type and depth."""
        selected_ai_type = self.ai_option_var.get()
        selected_ai_depth_str = self.ai_depth_var.get()
        selected_ai_depth = DEFAULT_AI_DEPTH
        try:
            selected_ai_depth = int(selected_ai_depth_str)
            if selected_ai_depth < 1:
                selected_ai_depth = 1
                tk.messagebox.showwarning("Invalid Input", "Depth cannot be less than 1. Using 1.")
            elif selected_ai_depth > MAX_AI_DEPTH:
                selected_ai_depth = MAX_AI_DEPTH
                tk.messagebox.showwarning("Invalid Input", f"Depth capped at {MAX_AI_DEPTH} for performance.")
        except ValueError:
            tk.messagebox.showwarning("Invalid Input",
                                      f"Invalid depth input: {selected_ai_depth_str}. Using default depth {DEFAULT_AI_DEPTH}.")
            print(f"Invalid depth input: {selected_ai_depth_str}. Using default depth {DEFAULT_AI_DEPTH}")
        self.menu_frame.pack_forget()
        self.game_frame.pack(expand=True, fill='both')
        self.game_manager.start_new_game(selected_ai_type, selected_ai_depth)

    def get_board_pixel_size(self):
        """Return the pixel size of the board."""
        return (BOARD_SIZE - 1) * CELL_SIZE + 2 * BOARD_PADDING

    def draw_board(self):
        """Draw the game board with grid lines and star points."""
        self.canvas.delete("all")
        board_pixel_size = self.get_board_pixel_size()
        for i in range(BOARD_SIZE):
            y = BOARD_PADDING + i * CELL_SIZE
            self.canvas.create_line(BOARD_PADDING, y, board_pixel_size - BOARD_PADDING, y, fill='black')
        for i in range(BOARD_SIZE):
            x = BOARD_PADDING + i * CELL_SIZE
            self.canvas.create_line(x, BOARD_PADDING, x, board_pixel_size - BOARD_PADDING, fill='black')
        star_points = []
        if BOARD_SIZE == 19:
            star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        for r, c in star_points:
            x = BOARD_PADDING + c * CELL_SIZE
            y = BOARD_PADDING + r * CELL_SIZE
            star_radius = 4
            self.canvas.create_oval(x - star_radius, y - star_radius, x + star_radius, y + star_radius, fill='black')

    def draw_stones(self, board_state, winning_line=None):
        """Draw all stones and highlight the winning line if provided."""
        self.canvas.delete("stone")
        self.canvas.delete("win_line")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                player = board_state[r][c]
                if player != EMPTY:
                    x = BOARD_PADDING + c * CELL_SIZE
                    y = BOARD_PADDING + r * CELL_SIZE
                    color = 'black' if player == PLAYER_1 else 'white'
                    outline = 'black' if player == PLAYER_2 else 'white'
                    if winning_line and (r, c) in winning_line:
                        outline = 'red'  # Highlight winning stones
                    self.canvas.create_oval(x - STONE_RADIUS, y - STONE_RADIUS,
                                            x + STONE_RADIUS, y + STONE_RADIUS,
                                            fill=color, outline=outline, tags="stone")
        if winning_line and len(winning_line) >= WIN_SEQUENCE:
            start_r, start_c = winning_line[0]
            end_r, end_c = winning_line[-1]
            start_x = BOARD_PADDING + start_c * CELL_SIZE
            start_y = BOARD_PADDING + start_r * CELL_SIZE
            end_x = BOARD_PADDING + end_c * CELL_SIZE
            end_y = BOARD_PADDING + end_r * CELL_SIZE
            self.canvas.create_line(start_x, start_y, end_x, end_y, fill='red', width=3, tags="win_line")

    def canvas_click(self, event):
        """Handle mouse clicks on the canvas to place stones."""
        col = int((event.x - BOARD_PADDING) / CELL_SIZE + 0.5)
        row = int((event.y - BOARD_PADDING) / CELL_SIZE + 0.5)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            x_check = BOARD_PADDING + col * CELL_SIZE
            y_check = BOARD_PADDING + row * CELL_SIZE
            distance = math.dist((event.x, event.y), (x_check, y_check))
            if distance < CELL_SIZE / 2:
                self.game_manager.handle_player_move(row, col)
            else:
                self.status_label.config(text="Click was not close enough to an intersection.")
                print("Click was not close enough to an intersection.")
        else:
            self.status_label.config(text="Click was outside board bounds.")
            print("Click was outside board bounds.")

    def update_display(self, board_state, status_message, winning_line=None):
        """Update the board display and status message."""
        self.draw_stones(board_state, winning_line)
        self.status_label.config(text=status_message)
        self.root.update_idletasks()

    def display_timer(self, time_taken):
        """Display the time taken for the AI's move."""
        self.timer_label.config(text=f"AI time: {time_taken:.6f} seconds")

    def disable_input(self):
        """Disable canvas input and buttons during AI moves."""
        self.canvas.unbind("<Button-1>")
        self.undo_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.load_button.config(state='disabled')

    def enable_input(self):
        """Enable canvas input and buttons for player moves."""
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.undo_button.config(state='normal' if self.game_manager.can_undo() else 'disabled')
        self.save_button.config(state='normal')
        self.load_button.config(state='normal')

    def show_game_over(self, message, winning_line=None):
        """Display the game over message and show the main menu button."""
        self.status_label.config(text=message)
        self.draw_stones(self.game_manager.board.board, winning_line)
        self.disable_input()
        self.menu_button.pack(pady=10)


# --- Game Manager Class ---

class GameManager:
    def __init__(self):
        """Initialize the game manager."""
        self.board = None
        self.gui = None
        self.current_player = PLAYER_1
        self.ai_type = None
        self.ai_depth = None
        self.game_over = False
        self.player1_first_move = True
        self.current_turn_moves = []
        self.state_history = []

    def set_gui(self, gui):
        """Set the GUI for the game manager."""
        self.gui = gui

    def start_new_game(self, ai_type, ai_depth):
        """Start a new game with the specified AI type and depth."""
        self.board = Board(BOARD_SIZE)
        self.current_player = PLAYER_1
        self.ai_type = ai_type
        self.ai_depth = ai_depth
        self.game_over = False
        self.player1_first_move = True
        self.current_turn_moves = []
        self.state_history = []
        self.gui.draw_board()
        self.gui.update_display(self.board.board, f"Game started. Player {self.current_player}'s turn (place 1 stone).")
        self.gui.enable_input()
        self.gui.display_timer(0.0)

    def save_state(self):
        """Save the current game state for potential undo."""
        state = {
            'board': self.board.copy(),
            'current_player': self.current_player,
            'player1_first_move': self.player1_first_move,
            'current_turn_moves': self.current_turn_moves.copy(),
            'game_over': self.game_over
        }
        self.state_history.append(state)

    def can_undo(self):
        """Check if an undo is possible."""
        return len(self.state_history) > 0 and self.current_player == PLAYER_1 and not self.game_over

    def undo_move(self):
        """Undo the last player turn and restore the previous state."""
        if not self.can_undo():
            tk.messagebox.showinfo("Cannot Undo", "No moves to undo or not your turn.")
            return
        state = self.state_history.pop()
        self.board = state['board']
        self.current_player = state['current_player']
        self.player1_first_move = state['player1_first_move']
        self.current_turn_moves = state['current_turn_moves']
        self.game_over = state['game_over']
        status_message = f"Player {self.current_player}'s turn (place {'1 stone' if self.player1_first_move else '2 stones'}{' - stone 2' if len(self.current_turn_moves) == 1 else ''})."
        self.gui.update_display(self.board.board, status_message)
        self.gui.enable_input()

    def save_game(self):
        """Save the current game state to a file."""
        if self.game_over:
            tk.messagebox.showinfo("Cannot Save", "Cannot save a finished game.")
            return
        game_state = {
            'board': self.board.board,
            'current_player': self.current_player,
            'ai_type': self.ai_type,
            'ai_depth': self.ai_depth,
            'player1_first_move': self.player1_first_move,
            'current_turn_moves': self.current_turn_moves,
            'state_history': self.state_history,
            'game_over': self.game_over
        }
        try:
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(game_state, f)
            tk.messagebox.showinfo("Save Game", "Game saved successfully.")
            print("Game saved successfully.")
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Failed to save game: {str(e)}")
            print(f"Failed to save game: {str(e)}")

    def load_game(self):
        """Load a game state from a file."""
        if not os.path.exists(SAVE_FILE):
            tk.messagebox.showinfo("Load Game", "No saved game found.")
            print("No saved game found.")
            return
        try:
            with open(SAVE_FILE, 'rb') as f:
                game_state = pickle.load(f)
            self.board = Board(BOARD_SIZE)
            self.board.board = game_state['board']
            self.current_player = game_state['current_player']
            self.ai_type = game_state['ai_type']
            self.ai_depth = game_state['ai_depth']
            self.player1_first_move = game_state['player1_first_move']
            self.current_turn_moves = game_state['current_turn_moves']
            self.state_history = game_state['state_history']
            self.game_over = game_state['game_over']
            self.gui.menu_frame.pack_forget()
            self.gui.game_frame.pack(expand=True, fill='both')
            self.gui.draw_board()
            status_message = f"Player {self.current_player}'s turn (place {'1 stone' if self.player1_first_move else '2 stones'}{' - stone 2' if len(self.current_turn_moves) == 1 else ''})."
            if self.game_over:
                status_message = "Game over. Return to main menu."
                self.gui.show_game_over(status_message)
            else:
                self.gui.update_display(self.board.board, status_message)
                if self.current_player == PLAYER_1:
                    self.gui.enable_input()
                else:
                    self.gui.disable_input()
                    self.gui.root.after(100, self.trigger_ai_move)
            tk.messagebox.showinfo("Load Game", "Game loaded successfully.")
            print("Game loaded successfully.")
        except Exception as e:
            tk.messagebox.showerror("Load Error", f"Failed to load game: {str(e)}")
            print(f"Failed to load game: {str(e)}")

    def handle_player_move(self, row, col):
        """Handle a player's move at (row, col)."""
        if self.game_over or self.current_player != PLAYER_1:
            return
        if self.board.is_valid_move(row, col):
            if self.player1_first_move or len(self.current_turn_moves) == 0:
                self.save_state()
            if self.player1_first_move:
                self.board.make_move(row, col, PLAYER_1)
                self.gui.update_display(self.board.board, "Player 1 placed first stone.")
                self.player1_first_move = False
                win, winning_line = self.board.check_win(row, col, PLAYER_1)
                if win:
                    self.end_game(f"Player {PLAYER_1} wins!", winning_line)
                    return
                self.switch_player()
                self.trigger_ai_move()
            else:
                self.board.make_move(row, col, PLAYER_1)
                self.current_turn_moves.append((row, col))
                if len(self.current_turn_moves) == 1:
                    self.gui.update_display(self.board.board,
                                            f"Player {self.current_player} placed stone 1. Place stone 2.")
                    win, winning_line = self.board.check_win(row, col, PLAYER_1)
                    if win:
                        self.end_game(f"Player {PLAYER_1} wins!", winning_line)
                        return
                elif len(self.current_turn_moves) == 2:
                    self.gui.update_display(self.board.board, f"Player {self.current_player} placed stone 2.")
                    win, winning_line = self.board.check_win(row, col, PLAYER_1)
                    if win:
                        self.end_game(f"Player {PLAYER_1} wins!", winning_line)
                        return
                    if self.board.is_board_full():
                        self.end_game("It's a tie!")
                        return
                    self.current_turn_moves = []
                    self.switch_player()
                    self.trigger_ai_move()
        else:
            print("Invalid move.")

    def trigger_ai_move(self):
        """Trigger the AI to make its move."""
        if self.game_over or self.current_player != PLAYER_2:
            return
        self.gui.disable_input()
        self.gui.update_display(self.board.board, f"Player {self.current_player} (AI) is thinking...")
        ai_move_pair, time_taken = select_ai_move(self.board, self.ai_type, self.ai_depth)
        self.gui.display_timer(time_taken)
        if ai_move_pair is None:
            print("AI could not find a move.")
            self.end_game("Game ended (AI could not move).")
            return
        move1, move2 = ai_move_pair
        if self.board.make_move(move1[0], move1[1], PLAYER_2):
            self.gui.update_display(self.board.board, f"Player {self.current_player} (AI) placed stone 1.")
            win, winning_line = self.board.check_win(move1[0], move1[1], PLAYER_2)
            if win:
                self.end_game(f"Player {PLAYER_2} (AI) wins!", winning_line)
                return
        else:
            print(f"AI selected invalid move 1: {move1}")
            self.end_game("Game ended due to AI error (invalid move 1).")
            return
        if self.board.is_valid_move(move2[0], move2[1]):
            self.board.make_move(move2[0], move2[1], PLAYER_2)
            self.gui.update_display(self.board.board, f"Player {self.current_player} (AI) placed stone 2.")
            win, winning_line = self.board.check_win(move2[0], move2[1], PLAYER_2)
            if win:
                self.end_game(f"Player {PLAYER_2} (AI) wins!", winning_line)
                return
        else:
            print(f"AI selected invalid move 2: {move2}")
            self.end_game("Game ended due to AI error (invalid move 2).")
            return
        if self.board.is_board_full():
            self.end_game("It's a tie!")
            return
        self.switch_player()
        self.gui.enable_input()
        self.gui.update_display(self.board.board, f"Player {self.current_player}'s turn (place 2 stones).")

    def switch_player(self):
        """Switch the current player."""
        self.current_player = PLAYER_1 if self.current_player == PLAYER_2 else PLAYER_2

    def end_game(self, message, winning_line=None):
        """End the game with the given message and optional winning line."""
        self.game_over = True
        self.gui.show_game_over(message, winning_line)
        tk.messagebox.showinfo("Game Over", message)
        print(message)


# --- Main Function ---

def main():
    """Start the Connect 6 game."""
    root = tk.Tk()
    root.title("Connect 6")
    game_manager = GameManager()
    gui = GameGUI(root, game_manager)
    game_manager.set_gui(gui)
    gui.show_main_menu()
    root.mainloop()


if __name__ == "__main__":
    main()