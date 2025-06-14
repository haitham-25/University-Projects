# Connect 6 Game

Connect 6 is a strategic board game implemented in Python with a Tkinter-based GUI, allowing a human player to compete against an AI opponent powered by multiple advanced algorithms. This project demonstrates complex game logic, AI decision making, and graphical interface design in Python.

---

## Table of Contents

1. [Introduction](#introduction)  
2. [Game Background and Rules](#game-background-and-rules)  
3. [Project Overview](#project-overview)  
4. [Key Features](#key-features)  
5. [Technical Architecture](#technical-architecture)  
6. [AI Algorithms Explained](#ai-algorithms-explained)  
7. [User Interface and Experience](#user-interface-and-experience)  
8. [Installation and Setup](#installation-and-setup)  
9. [How to Play](#how-to-play)  
10. [Code Structure and Components](#code-structure-and-components)  
11. [Extending and Customizing the Game](#extending-and-customizing-the-game)  
12. [Known Issues and Troubleshooting](#known-issues-and-troubleshooting)  
13. [Future Enhancements](#future-enhancements)  
14. [Contributing Guidelines](#contributing-guidelines)  
15. [License](#license)  
16. [Acknowledgments and Contact](#acknowledgments-and-contact)  

---

## Introduction

Connect 6 is a two-player connection board game that is a variation of the popular Connect 4. Played on a 19x19 grid, players aim to create a continuous line of six stones horizontally, vertically, or diagonally. The game demands strategic planning and foresight, especially when competing against an intelligent AI.

This project implements Connect 6 with:

- An interactive GUI for smooth gameplay.
- AI opponents leveraging Minimax, Alpha-Beta pruning, and heuristic evaluations.
- Features to manage game flow, including move validation, win detection, and input handling.

This README provides a detailed guide to understanding, running, and extending the game.

---

## Game Background and Rules

- **Board Size:** 19x19 grid.
- **Starting Move:** Player 1 places one stone in the first move.
- **Subsequent Moves:** Each turn thereafter, players place two stones.
- **Objective:** Be the first to form an unbroken chain of six stones.
- **Winning Conditions:** Horizontal, vertical, or diagonal line of 6.
- **Game End:** Victory, or tie if the board is completely filled with no winner.

The rule modification of placing two stones per turn creates richer strategic depth and faster gameplay progression compared to traditional connect games.

---

## Project Overview

This Python project encapsulates:

- **Game Logic:** Manages board state, player turns, move validation, and win/tie conditions.
- **AI Engine:** Implements multiple algorithms allowing configurable AI difficulty and style.
- **GUI Layer:** Provides an intuitive interface using Tkinter with responsive visuals.
- **User Interaction:** Clickable board cells, AI move animation, and game status messages.
- **Error Handling:** Safeguards against invalid moves and AI errors, ensuring graceful game termination.

The design follows modular principles for easy maintenance and extensibility.

---

## Key Features

- **Interactive GUI:** Users can click to place stones; AI moves are visually updated.
- **Multiple AI Strategies:**  
  - *Minimax:* Exhaustive search to evaluate possible outcomes.  
  - *Alpha-Beta Pruning:* Efficient search by pruning suboptimal branches.  
  - *Heuristic-based:* Faster decision-making using board evaluation heuristics.
- **Dynamic Feedback:** Displays AI computation time and current game status.
- **Game State Management:** Detects wins, ties, and invalid moves robustly.
- **Input Control:** Player input disabled during AI turns to prevent conflicts.
- **Detailed Logging:** Prints debug info and AI decisions in the console for transparency.

---

## Technical Architecture

- **GameManager:** Orchestrates game state transitions, player turns, AI triggers.
- **Board:** Handles internal board representation, move validation, win checks.
- **AI Module:** Contains algorithms to evaluate and select moves.
- **GUI Module:** Uses Tkinter for windows, buttons, labels, and canvas rendering.
- **Main Script:** Entry point initializing the game window and connecting modules.

The game uses an event-driven approach, responding to user clicks and AI computations asynchronously.

---

## AI Algorithms Explained

### Minimax

A depth-limited search algorithm exploring all possible moves to a certain depth, simulating alternating player moves. It assigns scores based on the likelihood of winning, assuming both players play optimally.

### Alpha-Beta Pruning

Optimizes Minimax by pruning branches that cannot influence the final decision. This drastically reduces the number of nodes evaluated, allowing deeper searches or faster move decisions.

### Heuristic Evaluation

Instead of exhaustive search, uses board evaluation functions considering factors such as:

- Open lines of stones.
- Threats and potential wins.
- Blocking opponent’s winning opportunities.
- Favoring center board control.

The heuristics provide a balance between performance and intelligence.

---

## User Interface and Experience

- **Main Menu:** Start game, select AI difficulty, exit.
- **Board Display:** Visual 19x19 grid showing player and AI stones.
- **Status Updates:** Labels indicating current player, AI thinking, and game results.
- **Move Highlighting:** Optional feature to highlight winning lines.
- **Input Control:** Prevents user clicks during AI calculations to avoid errors.

The UI aims to be user-friendly and informative.

---

## Installation and Setup

### Requirements

- Python 3.6+
- Tkinter (standard with most Python distributions)

### Installation Steps

1. Clone or download the repository.
2. Ensure Python and Tkinter are installed (`python -m tkinter` should open a test window).
3. Run the game:

```bash
python main.py
