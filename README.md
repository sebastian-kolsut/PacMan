*This project has been created as part of the 42 curriculum by ndemkiv and skolsut.*

# Pac-Man 42 Project

## Description

Pac-Man 42 Project is a Python implementation of a Pac-Man-style arcade game. The player controls Pac-Man inside a procedurally generated maze, collects pacgums, avoids ghosts, uses super pacgums to make ghosts edible, progresses through multiple levels, and saves final scores to a persistent highscore table.

The game includes a graphical interface, main menu, instructions screen, pause menu, settings screen, highscores screen, win/lose screen, music, configurable gameplay values, and cheat controls.

## Features

- Procedurally generated mazes using the provided A-Maze-ing package
- At least 10 configurable levels
- Fixed seed for the first level and random seeds for later levels
- Pac-Man movement with both WASD and arrow keys
- Regular pacgums and four super pacgums placed in the maze corners
- Four ghosts: Blinky, Clyde, Pinky, and Inky
- Frightened ghost mode after eating a super pacgum
- Score, lives, current level, and timer displayed in the HUD
- Persistent top-10 highscore table
- Main menu with Start, Instructions, Highscores, Settings, and Exit
- Pause menu with Resume, Restart, Settings, and Main Menu
- Win/Lose screen with final score and player name input
- Settings screen for wall color and music volume
- Background music with graceful fallback if audio is unavailable
- Cheat mode controls for testing and evaluation
- JSON configuration file with comment support
- Makefile commands for install, run, debug, clean, and lint
- Packaging configuration through `PacMan.spec`

## Requirements

- Python 3.10 or higher
- `uv`
- MLX package provided in the project wheels
- A-Maze-ing package provided in the project wheels
- Project dependencies from `pyproject.toml`

## Installation

Install dependencies with:

```bash
make install
```

or directly with:

```bash
uv sync
```

## Running the Game

Run the game with:

```bash
make run
```

or directly with:

```bash
uv run python3 pac-man.py config.json
```

The game expects exactly one configuration file argument:

```bash
python3 pac-man.py config.json
```

If the argument is missing, invalid, or not a JSON file, the game prints a clear error message instead of a raw traceback.

## Controls

### Gameplay

| Key | Action |
|---|---|
| `W` / Arrow Up | Move up |
| `A` / Arrow Left | Move left |
| `S` / Arrow Down | Move down |
| `D` / Arrow Right | Move right |
| `Esc` | Pause the game |

### Menus

| Key | Action |
|---|---|
| `W` / Arrow Up | Move selection up |
| `S` / Arrow Down | Move selection down |
| `Enter` / `Space` | Confirm selection |
| `Esc` | Return or close current screen |

### Cheat Mode

| Key | Cheat |
|---|---|
| `F1` | Toggle invincibility |
| `F2` | Toggle ghost freeze |
| `F3` | Add one extra life |
| `F4` | Toggle fast Pac-Man speed |
| `F5` | Skip current level |

After any cheat key is pressed, the HUD displays the available cheat controls.

## Configuration

The game is configured through a JSON file, usually `config.json`.

Example:

```json
{
  "highscore_filename": "highscores.json",
  "lives": 3,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 100,
  "seed": 42,
  "levels": [
    {
      "width": 15,
      "height": 15,
      "pacgum": 80,
      "level_max_time": 180
    }
  ]
}
```

### Supported Config Fields

| Field | Meaning |
|---|---|
| `highscore_filename` | JSON file used to store highscores |
| `lives` | Starting number of player lives |
| `points_per_pacgum` | Points for a regular pacgum |
| `points_per_super_pacgum` | Points for a super pacgum |
| `points_per_ghost` | Points for eating a frightened ghost |
| `seed` | Fixed seed used for the first level |
| `levels` | List of level configurations |

Each level contains:

| Field | Meaning |
|---|---|
| `width` | Maze width in cells |
| `height` | Maze height in cells |
| `pacgum` | Number of regular pacgums |
| `level_max_time` | Time limit for the level in seconds |

The parser supports comments using `#` and `//`. Invalid or unsafe values are clamped to safe defaults where possible.

## Maze Generation

The maze is generated using the provided A-Maze-ing package.

The game uses:

```python
perfect=False
```

This is important for Pac-Man gameplay because a perfect maze has only one path between any two cells. Pac-Man-style gameplay needs loops and alternative paths so the player can escape ghosts.

The first level uses the fixed `seed` from the configuration file. Later levels use random seeds to make the game less repetitive.

The maze data is converted into directional bitboards for faster collision checks and rendering.

## Gameplay Rules

- Pac-Man starts near the center of the maze.
- Four ghosts start in the maze corners.
- Regular pacgums increase the score.
- Super pacgums are placed in the four corners.
- Eating a super pacgum makes ghosts frightened and edible for a limited time.
- Touching a normal ghost removes one life.
- Touching a frightened ghost eats the ghost and increases the score.
- The level is completed when all pacgums and super pacgums are collected.
- The game is won after completing all configured levels.
- The game is lost when the player loses all lives or the level timer reaches zero.

## Highscores

Highscores are stored in a JSON file defined by `highscore_filename`.

Rules:

- Only the top 10 scores are stored.
- Scores are sorted from highest to lowest.
- Player names are limited to 10 characters.
- Player names may contain alphanumeric characters and spaces.
- Negative scores are rejected.
- If the highscore file is missing or invalid, the game creates or uses an empty leaderboard.

## Architecture

The project is organized around separate screens and gameplay components.

### Main Files

| File | Purpose |
|---|---|
| `pac-man.py` | CLI entry point |
| `src/MainGameLoop.py` | Main MLX loop and screen routing |
| `src/Parser.py` | Config parser with comment support |
| `src/models/config_models.py` | Pydantic config validation |
| `src/Highscores.py` | Persistent highscore handling |
| `src/MusicPlayer.py` | Background music management |

### Screens

| Screen | File |
|---|---|
| Main menu | `src/screens/MainMenu.py` |
| Gameplay | `src/screens/PlayGame.py` |
| Instructions | `src/screens/InstructionsScreen.py` |
| Highscores | `src/screens/HighscoresScreen.py` |
| Settings | `src/screens/SettingsScreen.py` |
| Win/Lose | `src/screens/WinLoseScreen.py` |

### Gameplay Components

| Component | File |
|---|---|
| Maze | `src/screens/game/Maze.py` |
| Maze rendering | `src/screens/game/RenderMaze.py` |
| Pac-Man | `src/screens/game/PacMan.py` |
| Pacgums | `src/screens/game/Pacgums.py` |
| Ghost base class | `src/screens/game/ghosts/Ghost.py` |
| Ghost state | `src/screens/game/ghosts/GhostState.py` |
| Pathfinding | `src/screens/game/Pathfinder.py` |
| HUD | `src/screens/game/HUD/HUD.py` |

## Rendering

Rendering is handled through a custom `FrameBuffer` class.

Important rendering utilities:

- `draw_blended_tile` for alpha-blended sprites and text
- `draw_clipped` for safe drawing when an asset may go partly outside the screen
- `get_image_array` for loading and resizing image assets

Text rendering is handled by `RenderText`, which rasterizes font characters into image arrays.

## Project Management

Project management documentation is stored in:

```text
project_management/
```

Recommended files:

| File | Purpose |
|---|---|
| `timeline.md` | Planned and actual project progress |
| `kanban.md` | GitHub-based Kanban workflow and task summary |
| `risks.md` | Main risks and mitigation strategies |
| `acceptance_tests.md` | Manual acceptance test plan |
| `technical_choices.md` | Explanation of major technical decisions |

GitHub branches and pull requests were used to separate features, review changes, and reduce merge conflicts.

## Testing

Run Python compile checks manually with:

```bash
uv run python3 -m py_compile pac-man.py src/MainGameLoop.py src/Parser.py
```

Run linting with:

```bash
make lint
```

## Makefile Commands

| Command | Purpose |
|---|---|
| `make install` | Install dependencies |
| `make run` | Run the game with `config.json` |
| `make debug` | Run the game in debugger mode |
| `make clean` | Remove cache files |
| `make lint` | Run code quality checks |

## Packaging

The repository includes:

```text
PacMan.spec
```

This file is used to prepare a packaged version of the game. Before final submission, the packaged build should be tested to ensure that images, fonts, music, config files, and other assets are included correctly.

## Resources and AI Usage

Resources used in the project:

- The provided A-Maze-ing package
- MLX for graphics/window handling
- Pygame mixer for music playback
- Pydantic for config and highscore validation
- NumPy and Pillow for image processing

AI assistance was used for code review, documentation drafting, debugging ideas, and wording improvements. Final implementation decisions, testing, and integration were handled by the project team.

## Known Limitations

- Some systems may not have an available audio device. In that case, the game disables music and continues normally.
- The config parser strips `#` and `//` comments line by line, so strings containing `//` should be avoided in config values.
- Visual layout should be checked on different screen sizes before final submission.

## Final Submission Checklist

Before submission:

- [ ] `make install` works
- [ ] `make run` starts the game
- [ ] `make lint` passes or known issues are fixed
- [ ] `config.json` contains at least 10 levels
- [ ] Invalid config values do not crash the game
- [ ] Highscores are saved and displayed correctly
- [ ] Main menu, instructions, highscores, settings, pause, win, and lose screens work
- [ ] Cheat mode works with F1-F5
- [ ] Project management files are present
- [ ] Packaged build has been tested
