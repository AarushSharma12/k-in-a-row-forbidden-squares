# K‑in‑a‑Row with Forbidden Squares

![Python](https://img.shields.io/badge/python-3.9%2B-blue)

A Python framework for playing and experimenting with K‑in‑a‑Row games (e.g., Tic‑Tac‑Toe, 5‑in‑a‑Row) on boards that may include forbidden squares. It ships with multiple agents, an offline game master, optional HTML rendering, and an AI agent featuring alpha‑beta pruning, move ordering, and Zobrist hashing.

## Why This Is Useful

- **Pluggable agents:** Swap in different strategies with minimal configuration.
- **Multiple game variants:** TTT, 5‑in‑a‑Row with blocked corners, Cassini—ready out of the box.
- **Extensible architecture:** Clear entry points for custom search algorithms and heuristics.
- **HTML export:** Generate visual game reports for analysis and presentation.
- **Lightweight dependencies:** Simple, dependency‑light code designed for easy extension.

## 🧠 AI Architecture

The core agent (`KInARow.py`) implements a high-performance adversarial search engine:

- **Minimax with Alpha-Beta Pruning:** Optimizes decision depth by pruning irrelevant branches.
- **Iterative Deepening & Move Ordering:** Prioritizes promising moves (e.g., center control, winning threats) to maximize pruning efficiency.
- **Zobrist Hashing:** Uses a Transposition Table to cache board states ($O(1)$ lookup), preventing redundant calculations for identical states reached via different move orders.
- **LLM Integration:** Connects to Google's Gemini API to generate dynamic, persona-based commentary on the game state.

## Getting Started

### Prerequisites

- Python 3.9+ recommended.
- Optional (for dynamic utterances): `google-generativeai` and an API key.

### Clone and Run

```bash
# From repository root
python src/Game_Master_Offline.py
```

This launches a Tic‑Tac‑Toe match: Bruh (alpha‑beta agent) vs Randy (random agent). The console displays the game progression, and an HTML report is generated if enabled.

### Switch Game Variants

Select from built‑in variants defined in `src/game_types.py`:

- `TTT` — 3 in a row
- `FIAR` — 5 in a row on 7×7 with corners forbidden
- `Cassini` — 5 in a row with a ring of forbidden squares

Example:

```python
from game_types import TTT, FIAR, Cassini
import KInARow as bruh
import RandomPlayer as rand
from Game_Master_Offline import set_game, set_players, runGame

set_game(FIAR)  # Options: TTT, FIAR, Cassini

px = bruh.OurAgent()     # X = alpha-beta agent
po = rand.OurAgent()     # O = random agent

set_players(px, po)
runGame()
```

### HTML Output

- Controlled by `USE_HTML` in `src/Game_Master_Offline.py` (default: `True`).
- Output filename format: `<X>-vs-<O>-in-<Game>-round-<n>.html`.
- Requires the `img/` directory (containing X, O, gray, black images) alongside the output.

### LLM-Powered Utterances

The agent in `src/KInARow.py` generates in‑character remarks using Google's Gemini API:

1. Install the SDK:
   ```bash
   pip install google-generativeai
   ```
2. Create `src/app_secrets.py`:
   ```python
   GOOGLE_API_KEY = "YOUR_API_KEY"
   ```
   This file is git‑ignored by default.
3. The agent automatically attempts LLM integration and falls back gracefully if unavailable.

## Usage Examples

**Run the offline game master:**

```bash
python src/Game_Master_Offline.py
```

**Configure custom players:**

```python
from game_types import TTT
from Game_Master_Offline import set_game, set_players, runGame
from RandomPlayer import OurAgent as RandomAgent
from KInARow import OurAgent as BruhAgent

set_game(TTT)
set_players(BruhAgent(), RandomAgent())
runGame()
```

**Implement a custom agent** by subclassing `BaseGameAgent` in `src/agent_base.py` and overriding:

- `prepare(...)`
- `make_move(state, last_utterance, time_limit)`
- (optional) `minimax(...)`, `static_eval(...)`

## Project Structure

```
src/
  agent_base.py            # Base class for agents (BaseGameAgent)
  Game_Master_Offline.py   # Offline game engine (entry point)
  game_types.py            # Game variants and initial states
  gameToHTML.py            # HTML report rendering
  KInARow.py               # Alpha-beta + Zobrist agent ("Bruh")
  RandomPlayer.py          # Baseline random agent
  winTesterForK.py         # Win detection for K-in-a-row
  app_secrets.py           # (optional, git-ignored) API key for LLM
```

## Author

**Aarush Sharma**
