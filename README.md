# K-in-a-Row with Forbidden Squares

A Python-based framework for running, experimenting with, and extending a K-in-a-Row game (similar to Tic-Tac-Toe or Connect Four variants). This project supports multiple agents (both naive and AI-based) and includes an offline game master. Originally developed as a course assignment at the University of Washington.

## Features

- **Game Master**  
  Manages turn-taking, checks for wins, and controls the overall gameplay flow.

- **Multiple Agents**  
  - **Random Player**: Makes random moves.  
  - **Chaddington 'Bruh' Balding III** (Alpha-Beta + Zobrist agent): Demonstrates alpha-beta pruning, move ordering, and optional hashing.  
  - **Template Agent Base**: A starting point (in `agent_base.py`) for building your own custom AI.

- **Configurable Game Types**  
  Play standard Tic-Tac-Toe (3-in-a-row), 5-in-a-row with forbidden corners, or new variants by adjusting the parameters.

- **HTML Output**  
  Optionally export the game flow to an HTML file for easy visual reference.

## Directory & File Overview

- **`agent_base.py`**  
  Provides a base class `KAgent` that all agents can extend. Contains default stubs for `make_move`, `prepare`, `static_eval`, etc.

- **`Game_Master_Offline.py`**  
  The main offline game controller. Runs the match between two agents, handles turn-taking, and declares a winner or draw.

- **`game_types.py`**  
  Defines various game boards and rules (e.g., Tic-Tac-Toe `TTT`, Five-in-a-Row `FIAR`, Cassini, etc.). Each has:
  - Dimensions (`n` x `m`)
  - The value for K (how many in a row needed to win)
  - An initial state definition

- **`gameToHTML.py`**  
  Provides logic to render the board states to an HTML file with images representing X, O, and forbidden squares.

- **`RandomPlayer.py`**  
  A simple example agent that picks moves uniformly at random.

- **`winTesterForK.py`**  
  Contains a helper function to test if a given move creates a winning line of length K.

 **`KInARow.py`**  
  A more advanced agent demonstrating:
  - Alpha-beta pruning
  - Move ordering
  - Zobrist hashing
  - Basic persona-based text utterances

## Agent Name and Persona  
My agent is named **Chaddington "Bruh" Balding III**, an exaggerated "fratccent" character with loud, cocky, and party-centric speech. His persona includes references to seltzers, forced belches, and overconfidence in every utterance.

## The Twin Feature  
Implemented a `twin` parameter in the constructor. If `twin=True`, the agent's name appends `"2"` or `"II"` to distinguish itself when playing against a duplicate instance.

## Alpha-Beta Pruning Implementation  
Integrated into `minimax()` with `alpha` and `beta` parameters. When **β ≤ α** is detected, the search branch is pruned, reducing unnecessary evaluations.

### **Performance Results (Depth=3)**  
- **Baseline (No Ordering)**: ~3,000 static evaluations per turn.  
- **With Alpha-Beta & Move Ordering**: Reduced evaluations by **30-40%**, averaging ~1,800-2,100.  

## Persona Details  
The agent’s dialogue mimics an exaggerated frat bro stereotype. Speech includes slowed delivery, slurred words, burping, and bold overconfidence. Designed to be comedic or mildly irritating.

## Dialog Features for Game State Relevance  
- **Move Coordinates**: Announces `(row, col)`.  
- **Board Evaluation**: The agent boasts when winning, expresses uncertainty when losing, and remains casual otherwise.  
- **Transitions**: Includes phrases like *"I’m just getting warmed up!"* when neutral and mocks the opponent when leading.  

## Responsiveness to Opponent Remarks  
The agent detects keywords in the opponent's speech:  
- **"block" or "defense"** → Mocks opponent’s strategy.  
- **"win"** → Declares itself the game’s future legend.  
- **"Tell me how you did that"** → Provides a detailed statistical breakdown (**extra feature**).  
- **"What’s your take on the game so far?"** → Gives a summary of the game and predicts the winner (**extra feature**).  

## Dialog Development Process  
1. **Prototype**: Simple random quips.  
2. **State-Based Logic**: Integrated board evaluation.  
3. **Keyword Detection**: Responses adjusted dynamically.  
4. **Testing & Refinement**: Enhanced comedic tone while keeping speech concise.  

## Extra Features  

### **1. Move Ordering**  
Before recursion, moves are sorted based on `static_eval()`, prioritizing promising branches. This improves alpha-beta pruning efficiency.  

### **2. Zobrist Hashing**  
A 64-bit hash is computed for each board state to store and retrieve evaluations efficiently, reducing redundant computations.  

#### **Tracked metrics:**  
- **Writes**: New evaluations stored.  
- **Read Attempts**: Board states checked.  
- **Hits**: Previously seen states retrieved.  

### **3. "Tell me how you did that" (Extra-Credit)**  
When triggered by the opponent, the agent responds with:  
- Number of static evaluations performed  
- Alpha-beta cutoffs  
- Move computation time  
- Zobrist hashing stats  

### **4. "What’s your take on the game so far?" (Extra-Credit)**  
Provides:  
- A short narrative summary of the game  
- Turn count reference  
- A prediction on who might win based on `static_eval()`  
