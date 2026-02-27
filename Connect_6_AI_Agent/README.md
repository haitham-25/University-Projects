# Connect 6 — AI-Powered Board Game

A fully playable **Connect 6** game built in Python with a Tkinter GUI and multiple AI strategies to compete against. The game is played on a 19×19 Go-style board where the goal is to be the first to place **6 consecutive stones** in a row (horizontally, vertically, or diagonally).

---

## Table of Contents

- [Game Rules](#game-rules)
- [Features](#features)
- [Requirements](#requirements)
- [Installation & Running](#installation--running)
- [Project Structure](#project-structure)
- [Algorithms & AI Strategies](#algorithms--ai-strategies)
- [Heuristic Functions](#heuristic-functions)
- [Move Generation Strategies](#move-generation-strategies)
- [Save & Load](#save--load)
- [Logging](#logging)
- [Configuration Constants](#configuration-constants)

---

## Game Rules

- The board is **19×19** intersections.
- **Player 1 (Human/Black)** places **1 stone** on the very first move of the game.
- From turn 2 onward, **each player places 2 stones per turn**.
- The first player to get **6 or more consecutive stones** in a line wins.
- If the board fills up with no winner, it is a **tie**.

---

## Features

- Human vs. AI gameplay on a 19×19 board
- **8 selectable AI strategies** ranging from pure Minimax to symmetry-reduced search
- Configurable AI search depth (1–4)
- Undo support (for human player moves)
- Save and load game state (via `pickle`)
- AI move-time display
- Winning line highlighted on the board
- AI decision logging to `ai_moves.log`

---

## Requirements

| Package   | Purpose                        |
|-----------|--------------------------------|
| `tkinter` | GUI (bundled with Python)      |
| `pygame`  | Imported (audio/future use)    |
| `pickle`  | Game save/load                 |
| `logging` | AI move logging                |

Install any missing packages:
```bash
pip install pygame
```

> `tkinter` is included with standard Python installations. If missing on Linux: `sudo apt-get install python3-tk`

---

## Installation & Running

```bash
# Clone or download the project
git clone <repo-url>
cd connect6

# Run the game
python Connect6_game.py
```

---

## Project Structure

```
Connect6_game.py
│
├── Board                    # Board state, move validation, win detection
├── GameManager              # Game flow, undo, save/load, turn management
├── GameGUI                  # Tkinter GUI, canvas drawing, user input
│
├── AI Strategy Functions
│   ├── evaluate()                       # General board evaluation heuristic
│   ├── threat_focused_heuristic()       # Defensive-heavy heuristic
│   ├── heuristic_open_three()           # Open-3 focused heuristic
│   ├── alphabeta()                      # Minimax with Alpha-Beta pruning
│   ├── get_all_possible_pairs()         # Full move generation
│   ├── get_reduced_moves_pairs()        # Proximity-reduced move generation
│   └── get_symmetry_reduced_pairs()     # Symmetry-reduced move generation
│
├── select_ai_move()         # AI move orchestrator
└── main()                   # Entry point
```

---

## Algorithms & AI Strategies

The game provides **8 AI strategies**, selectable from the main menu:

### 1. Minimax Only
- Uses pure **Minimax** search with no pruning.
- Explores all possible move pairs up to the configured depth.
- Uses the general `evaluate()` heuristic.
- Slowest strategy — not recommended above depth 2 on a 19×19 board.

### 2. Minimax + Alpha-Beta *(default)*
- **Minimax with Alpha-Beta Pruning**: the standard game-tree search optimization.
- The alpha (`α`) value tracks the best score the maximizing player can guarantee; beta (`β`) tracks the best the minimizing player can guarantee.
- When `β ≤ α`, remaining branches are pruned — they cannot influence the final decision.
- Move pairs are **sorted by heuristic score before searching** so the best candidates are explored first, maximizing pruning effectiveness.
- Uses the general `evaluate()` heuristic.

### 3. Heuristic Block Threats *(Limited Search)*
- A **shallow search** (capped at depth 2) using the `threat_focused_heuristic`.
- Reduces the move space using `get_reduced_moves_pairs()` — only considers intersections near occupied stones.
- Prioritizes blocking opponent winning threats over aggressive play.

### 4. Minimax + Threat Heuristic
- Full-depth **Minimax + Alpha-Beta** using the `threat_focused_heuristic`.
- Combines deep search with a heuristic that heavily penalizes allowing opponent threats.

### 5. Heuristic Open Three *(Limited Search)*
- A **shallow search** (capped at depth 2) using the `heuristic_open_three` evaluation.
- Focuses on creating and blocking **open-ended sequences of 3 stones**, which are difficult to stop.
- Reduced move space via `get_reduced_moves_pairs()`.

### 6. Minimax + Open Three Heuristic
- Full-depth **Minimax + Alpha-Beta** combined with `heuristic_open_three`.
- Deep strategic search with a focus on open sequences.

### 7. Heuristic Reduction
- Full-depth **Minimax + Alpha-Beta** with `evaluate()`, but only searches moves near existing stones (`get_reduced_moves_pairs()`).
- A balance between search depth and move space reduction.

### 8. Symmetry Reduction
- Reduces the search space by **detecting board symmetries** (rotations and reflections).
- For each pair of candidate moves, all 8 symmetrically equivalent versions are computed: 0°, 90°, 180°, 270° rotations + horizontal, vertical, main-diagonal, and anti-diagonal reflections.
- Only the **best representative** from each symmetry group is kept for search.
- Falls back to threat-blocking if immediate dangers are detected.

---

## Heuristic Functions

### `evaluate(board, player)`
The general-purpose board scoring function:
- Scans all **6-cell windows** in 4 directions (horizontal, vertical, diagonal, anti-diagonal).
- Scores each window based on how many stones the player or opponent has in it.
- Windows blocked by the opponent score 0.
- **Open ends** (both sides free) multiply the score by 2×; a single open end multiplies by 1.5×.
- Weighted scoring table:

| Stones in Window | Player Weight | Opponent Penalty |
|------------------|--------------|-----------------|
| 1                | 1            | 1               |
| 2                | 10           | 20              |
| 3                | 100          | 500             |
| 4                | 5,000        | 20,000          |
| 5                | 1,000,000    | 50,000,000      |
| 6                | 10,000,000   | 10,000,000      |

### `threat_focused_heuristic(board, player)`
- Immediately returns `±10,000,000` if a winning/losing move is detected.
- Uses **higher opponent penalty weights** than `evaluate()` to prioritize defensive play.
- Open-ended threat lines are weighted up to **4×** their base value.

### `heuristic_open_three(board, player)`
- Calls `find_critical_threats()` first — if any exist, returns `-9,000,000` immediately to penalize the position.
- Gives a **5× bonus** to open-ended 3-stone sequences (a key strategic concept in Connect 6).
- Very high penalties for allowing 5-in-a-row opponent threats.

---

## Move Generation Strategies

### `get_all_possible_pairs(board)`
- Generates every possible pair of empty intersections: **O(n²)** where n = number of empty cells.
- Used by Minimax Only and Minimax + Alpha-Beta (pure).
- Extremely slow on a full 19×19 board — only practical at depth 1–2.

### `get_reduced_moves_pairs(board)`
- Only considers empty intersections within a **Manhattan distance of 3** from any occupied stone (`REDUCTION_RADIUS = 3`).
- Always includes intersections flagged as **critical threats**, ensuring blocks are never missed.
- Falls back to a center region on an empty board.
- Dramatically reduces the branching factor without sacrificing critical moves.

### `get_symmetry_reduced_pairs(board)`
- Applies the reduced move space (same as above), then groups pairs by their **8-fold board symmetry**.
- For each symmetry group, only the highest-scoring representative is kept.
- Returns immediately if a threat block or immediate win is found.

---

## Immediate Win / Block Detection in `select_ai_move()`

Before invoking any search tree, the AI always:

1. **Checks for immediate wins** — scans for positions where placing 2 stones completes a 6-in-a-row for the AI. Plays that move immediately if found.
2. **Checks for critical blocks** — scans for positions where the human player has 5-in-a-row with one open end, requiring an immediate block. Plays the block if found.
3. **Falls back to the configured search strategy** if no immediate win or block is required.

This design guarantees the AI never misses a winning move or an obvious forced defense.

---

## Save & Load

- **Save**: Serializes the full game state (board, current player, AI config, move history) to `connect6_save.pkl` using Python's `pickle` module.
- **Load**: Restores the saved state and resumes gameplay, re-triggering the AI if it was the AI's turn.
- Saving a finished game is blocked.

---

## Logging

All AI decisions are written to `ai_moves.log`:
- AI type, depth, score, and chosen move pair for each turn
- Immediate wins and critical blocks detected
- Warnings and errors for fallback moves

---

## Configuration Constants

| Constant           | Default               | Description                          |
|--------------------|-----------------------|--------------------------------------|
| `BOARD_SIZE`       | 19                    | Board grid size                      |
| `WIN_SEQUENCE`     | 6                     | Consecutive stones needed to win     |
| `CELL_SIZE`        | 30                    | Pixel size per cell                  |
| `DEFAULT_AI_DEPTH` | 2                     | Default Minimax search depth         |
| `MAX_AI_DEPTH`     | 4                     | Maximum allowed search depth         |
| `REDUCTION_RADIUS` | 3                     | Proximity radius for move reduction  |
| `SAVE_FILE`        | `connect6_save.pkl`   | Save file path                       |
