# K‑in‑a‑Row with Forbidden Squares

![Python](https://img.shields.io/badge/python-3.9%2B-blue)

A Python framework for playing and experimenting with K‑in‑a‑Row games (e.g., Tic‑Tac‑Toe, 5‑in‑a‑Row) on boards that may include forbidden squares. It ships with multiple agents, an offline game master, optional HTML rendering, and an example AI agent with alpha‑beta pruning, move ordering, and Zobrist hashing.

## Why this is useful

- Pluggable agents: swap in different strategies quickly.
- Multiple game types out of the box (TTT, 5‑in‑a‑Row with blocked corners, Cassini).
- Clear entry points for search algorithms and heuristics.
- Optional HTML export for quick visual game reviews.
- Simple, dependency‑light code that’s easy to extend.

## Getting started

### Prerequisites

- Python 3.9+ recommended.
- Optional (for dynamic utterances): `google-generativeai` and an API key.

### Clone and run a demo

```bash
# From repository root
python src/Game_Master_Offline.py
```

This runs a demo Tic‑Tac‑Toe match: Bruh (alpha‑beta agent) vs Randy (random agent). The console prints the game, and an HTML report is created if enabled.

### Switch game types

Edit or run code to choose the built‑in variants from `src/game_types.py`:

- `TTT` (3 in a row)
- `FIAR` (5 in a row on 7×7 with corners forbidden)
- `Cassini` (5 in a row with a ring of forbidden squares)

Minimal example:

```python
# run_ttt.py (example)
from game_types import TTT, FIAR, Cassini
import KInARow as bruh
import RandomPlayer as rand
from Game_Master_Offline import set_game, set_players, runGame

set_game(FIAR)  # choose TTT, FIAR, or Cassini

px = bruh.OurAgent()     # X = alpha-beta agent
po = rand.OurAgent()     # O = random agent

set_players(px, po)
runGame()
```

### HTML output

- Controlled by `USE_HTML` in `src/Game_Master_Offline.py` (default: True).
- Output filename: `<X>-vs-<O>-in-<Game>-round-<n>.html`.
- Uses images under `img/` (X, O, gray, black). Ensure that folder exists alongside the output.

### Optional LLM utterances

The agent in `src/KInARow.py` can generate short, in‑character remarks using Gemini if enabled:

1. Install the SDK:
   ```bash
   pip install google-generativeai
   ```
2. Create `src/app_secrets.py` with:
   ```python
   GOOGLE_API_KEY = "YOUR_API_KEY"
   ```
   Make sure this file is git‑ignored (already covered in `.gitignore`).
3. The agent will attempt LLM usage automatically and gracefully fall back if unavailable.

## Usage examples

- Run the offline game master demo:  
  `python src/Game_Master_Offline.py`

- Use custom players:

```python
from game_types import TTT
from Game_Master_Offline import set_game, set_players, runGame
from RandomPlayer import OurAgent as RandomAgent
from KInARow import OurAgent as BruhAgent

set_game(TTT)
set_players(BruhAgent(), RandomAgent())
runGame()
```

- Implement your own agent by subclassing `KAgent` in `src/agent_base.py` and overriding:
  - `prepare(...)`
  - `make_move(state, last_utterance, time_limit)`
  - (optional) `minimax(...)`, `static_eval(...)`


## Maintainers

- Maintainer: Aarush Sharma (author of `src/KInARow.py`)

## Project structure

```
src/
  agent_base.py            # Base class for agents
  Game_Master_Offline.py   # Offline game master (entry point)
  game_types.py            # Game variants and initial states
  gameToHTML.py            # HTML report rendering
  KInARow.py               # Alpha-beta + Zobrist agent ("Bruh")
  RandomPlayer.py          # Baseline random agent
  winTesterForK.py         # Win detection for K-in-a-row
  app_secrets.py           # (optional, git-ignored) API key for LLM
```