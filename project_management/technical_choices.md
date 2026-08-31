# Technical Choices

## 1. Project Overview

This project is a Pac-Man inspired game implemented in Python as part of the 42 curriculum.

The main technical goal was to create a complete playable game with generated mazes, graphical rendering, keyboard controls, score tracking, persistent highscores, multiple screens, configuration support, and a packaged build option.

The project is structured around a custom game loop, screen-based UI flow, generated maze data, and reusable rendering utilities.

## 2. Programming Language

The project is implemented in Python.

Python was chosen because it is required by the project subject and provides a good balance between readability, object-oriented design, fast iteration, and testing support.

The codebase uses classes to separate responsibilities between the main loop, screens, gameplay entities, rendering utilities, configuration models, and persistent data.

Main examples:

- `MainGameLoop` controls the active screen and routes keyboard input.
- `PlayGame` owns the active gameplay state.
- `PacMan`, `Ghost`, `Pacgums`, and `Maze` represent the main gameplay objects.
- `FrameBuffer` and `RenderText` handle low-level rendering utilities.

## 3. Graphics Library

The game uses MLX for window creation, image buffers, keyboard input, and rendering.

A custom `FrameBuffer` class was created on top of MLX image buffers. This makes rendering easier to control and allows the project to work directly with NumPy pixel arrays.

Important rendering utilities include:

- `draw_blended_tile` for alpha-blended images.
- `draw_clipped` for safe image drawing inside screen boundaries.
- `get_image_array` for loading and resizing image assets.
- `commit` and `put_image_to_window` for sending the rendered frame to the MLX window.

This approach gives direct control over the retro-style UI, sprites, HUD, menus, and overlays.

## 4. Rendering and Assets

The project uses image assets for most UI elements and character sprites.

Assets are stored under the `assets/` directory and include:

- Pac-Man animation frames.
- Ghost sprites.
- Blue ghost sprite for frightened mode.
- HUD labels.
- Main menu buttons.
- Win, lose, pause, settings, and instruction screen assets.
- Fonts.
- Music files.

The rendering system loads assets using relative paths from the project root. To make this stable, `pac-man.py` changes the working directory to the application directory before starting the game.

This prevents asset path issues when the game is launched from another directory or from a packaged executable.

## 5. Text Rendering

The project uses a custom `RenderText` class for drawing text.

Instead of relying on direct text drawing inside MLX, the game pre-renders ASCII characters from a font file into image arrays. Text is then composed from these pre-rendered character images.

This was chosen because it keeps the visual style consistent with the pixel/arcade design and makes text rendering compatible with the existing `FrameBuffer` drawing system.

Text rendering is used for:

- Score display.
- Timer display.
- FPS display.
- Level number.
- Cheat-code hints.
- Highscore names and scores.
- Win/Lose name and score input.
- Settings labels.

## 6. Maze Generation

The game uses the provided A-Maze-ing `MazeGenerator` package.

The generator is used with:

```python
perfect=False
```

This is an important choice for Pac-Man gameplay. A perfect maze has only one path between any two cells, which makes it less suitable for a chase game. Pac-Man needs alternative routes, loops, and escape possibilities.

Using `perfect=False` creates mazes with more possible paths, which improves gameplay and makes ghost chasing less predictable.

The first level uses the fixed seed from the config file. Later levels use random seeds.

This gives two benefits:

- The first level is reproducible.
- Later levels have more variation between runs.

## 7. Maze Representation

The generated maze is converted into directional bitboards.

The `Maze` class stores wall information in a `Bitboards` dataclass with four integer fields:

- `up`
- `right`
- `down`
- `left`

Each bit represents whether a wall exists for a specific cell and direction.

This representation was chosen because it makes wall checks fast and compact. Characters can quickly check whether movement in a direction is blocked.

The method `is_wall_direction()` is used by Pac-Man, ghosts, and pathfinding logic to determine whether movement is possible.

## 8. Pathfinding

Ghost movement uses a custom `Pathfinder` class.

The pathfinder uses breadth-first search to find reachable cells and shortest paths through the maze.

It provides methods such as:

- `find_path`
- `next_direction`
- `get_neighbor_cells`
- `get_valid_directions`
- `get_reachable_cells`

This keeps pathfinding separate from ghost logic and allows ghosts to choose directions based on the current maze structure.

## 9. Game Architecture

The game uses a screen-based architecture.

The active screen is stored in the shared `ProgramState` object. `MainGameLoop` checks this state every frame and delegates rendering or input handling to the correct screen.

Main screens include:

- Main menu.
- Gameplay screen.
- Instructions screen.
- Highscores screen.
- Win/Lose screen.
- Settings screen.

This structure was chosen to keep each screen independent and easier to maintain.

For example:

- `MainMenu` handles menu navigation.
- `PlayGame` handles the actual game.
- `PauseScreen` handles in-game pause actions.
- `SettingsScreen` handles wall color and music volume.
- `WinLoseScreen` handles final score display and name input.

## 10. Shared Program State

The project uses a shared `ProgramState` dataclass.

It stores global runtime state such as:

- Current screen.
- Current game state.
- Last frame time.
- Frame interval.
- Current level.
- Wall theme index.
- Music volume.

This avoids passing many separate values between unrelated objects and allows systems such as rendering, music, settings, and gameplay to coordinate through one shared state object.

## 11. Character Movement

Pac-Man and ghosts inherit from a shared `Character` base class.

The base class contains common movement logic, including:

- Cell-based positioning.
- Direction handling.
- Pending direction changes.
- Wall collision checks.
- Snapping to cell centers.
- Collision radius calculation.
- Resetting to the starting position.

This reduces duplicated movement code and keeps Pac-Man and ghost-specific behavior in their own classes.

## 12. Pac-Man Controls

Pac-Man supports both WASD and arrow-key movement.

The game reads the currently pressed movement key through the keyboard state, which allows smoother continuous movement than relying only on isolated key press events.

Supported movement controls:

- `W` or Arrow Up: move up.
- `A` or Arrow Left: move left.
- `S` or Arrow Down: move down.
- `D` or Arrow Right: move right.

## 13. Ghost Behavior

The game includes four ghosts:

- Blinky.
- Clyde.
- Pinky.
- Inky.

The shared `Ghost` class handles common ghost behavior, including rendering, movement, frightened mode, eaten state, speed changes, and collision state.

Each ghost starts in one of the maze corners.

When Pac-Man eats a super pacgum, ghosts enter frightened mode. In this mode they use the blue ghost sprite, move slower, and can be eaten by Pac-Man.

## 14. Frightened Ghost Mode

Frightened ghost mode is controlled by a timer in `PlayGame`.

When Pac-Man eats a super pacgum:

- The frightened timer starts.
- All non-eaten ghosts become frightened.
- Ghosts switch to the blue asset.
- Ghosts become edible.
- Pac-Man receives points for eating frightened ghosts.

Near the end of the frightened timer, ghosts start blinking to indicate that the mode is about to end.

This matches the expected Pac-Man behavior and gives players visual feedback.

## 15. Pacgums and Super Pacgums

Pacgums are stored as bitboards.

The `Pacgums` class keeps two layouts:

- Regular pacgums.
- Super pacgums.

Regular pacgums are randomly placed on available cells. Super pacgums are placed in the four maze corners.

This design makes checking and removing pacgums efficient. When Pac-Man enters a cell, the corresponding bit can be checked and cleared.

The level is completed when both pacgum layouts are empty.

## 16. Scoring

The score is managed through the HUD `Score` object.

Points are awarded for:

- Eating regular pacgums.
- Eating super pacgums.
- Eating frightened ghosts.

Point values come from the config file.

The score is only increased and is not reduced during gameplay.

## 17. Lives

The player starts with the number of lives defined in the config file.

When Pac-Man collides with a normal ghost, one life is removed. If lives reach zero, the game switches to the Win/Lose screen with the lost state.

If cheat mode adds more lives than the initial maximum, the HUD displays one heart with a counter instead of drawing an unlimited number of hearts.

This keeps the HUD compact and readable.

## 18. Configuration

The game is launched with a JSON config file:

```bash
python3 pac-man.py config.json
```

The parser supports comments using `#` and `//`.

The config is validated using Pydantic models.

Important config fields include:

- `highscore_filename`
- `lives`
- `points_per_pacgum`
- `points_per_super_pacgum`
- `points_per_ghost`
- `seed`
- `levels`

Each level contains:

- `width`
- `height`
- `pacgum`
- `level_max_time`

Pydantic validators are used to replace invalid values with safe defaults or clamp them to safe ranges. This helps prevent crashes if the evaluator changes the config file.

## 19. CLI Startup

The entry point is `pac-man.py`.

The game expects exactly one config argument.

Example:

```bash
python3 pac-man.py config.json
```

The script resolves the config path before changing the working directory. This keeps relative config paths working while also allowing asset paths to be resolved from the project root.

Startup errors are caught and printed as clean messages instead of raw tracebacks.

## 20. Highscores

Highscores are stored in a JSON file.

The `Highscores` class loads, validates, sorts, and writes the leaderboard.

The leaderboard keeps only the top 10 scores.

Player names are limited to 10 characters and may contain alphanumeric characters and spaces.

If the highscore file is missing or invalid, the game creates or uses an empty leaderboard instead of crashing.

## 21. Win/Lose Flow

When the player loses all lives, runs out of time, or completes all levels, the game switches to the Win/Lose screen.

The Win/Lose screen displays:

- Game Over or You Won header.
- Final score.
- Name input if the score is eligible for the leaderboard.
- Restart, main menu, highscores, or settings actions depending on the state.

This creates a complete game loop from menu to gameplay to final score handling.

## 22. Cheat Mode

Cheat mode was added for testing, debugging, and subject requirements.

Cheat controls:

- F1: Toggle invincibility.
- F2: Toggle ghost freeze.
- F3: Add an extra life.
- F4: Toggle faster Pac-Man speed.
- F5: Skip the current level.

Once a cheat key is pressed, the HUD shows a cheat-code legend.

This makes the cheat functionality visible and easier to verify during evaluation.

## 23. Pause Screen

The game includes an in-game pause screen.

The pause screen allows the player to:

- Resume the game.
- Restart the game.
- Open settings.
- Return to the main menu.

The pause screen is rendered over the current gameplay frame with a dark overlay.

## 24. Settings Screen

The settings screen allows the player to change:

- Maze wall color.
- Music volume.

Wall color is stored in `ProgramState.wall_theme_index`.
Music volume is stored in `ProgramState.music_volume`.

The settings screen can be opened from the main menu or from the pause screen.

## 25. Music

Background music is handled with `pygame.mixer`.

Different tracks are used for menu screens and gameplay.

If no audio device is available, music is disabled gracefully and the game continues running.

This prevents the game from crashing in environments without sound support, such as virtual machines, Docker containers, or school computers with disabled audio devices.

## 26. Makefile

The project includes a `Makefile` to standardize common commands.

Typical targets include:

- `install` for dependency installation.
- `run` for launching the game.
- `debug` for debugging.
- `clean` for removing cache files.
- `lint` for code quality checks.

Using a Makefile makes the project easier to evaluate because the expected commands are documented and repeatable.

## 27. Testing

The project includes a `tests/` directory with unit tests for selected components.

Tests cover areas such as:

- Parsing.
- Highscores.
- Ghost state.
- Rendering helpers.
- Main loop initialization.
- Maze rendering behavior.

Manual acceptance testing is also used for gameplay behavior, UI navigation, cheat mode, settings, and packaging.

## 28. Packaging

The project includes a `PacMan.spec` file for packaging.

The goal of packaging is to create a distributable version of the game with Python code and assets included.

Packaging requires special attention because the game depends on image assets, fonts, music files, and local wheel files.

The startup script changes the working directory to the application directory to make packaged asset loading more reliable.

## 29. Error Handling

The project tries to avoid raw tracebacks during normal use.

Examples of error handling include:

- Invalid config filename handling.
- Invalid config value clamping.
- Missing or invalid highscore file fallback.
- Audio device failure fallback.
- Safe clipped drawing for UI elements.
- Game loop exception handling.

This improves robustness, especially because the evaluator may change configuration values or run the game in a different environment.

## 30. Summary

The main technical choices were focused on making the game playable, modular, visually consistent, and robust.

Key decisions:

- Use Python with object-oriented design.
- Use MLX with custom frame buffers for rendering.
- Use the provided A-Maze-ing generator with `perfect=False`.
- Store maze walls as bitboards for efficient collision checks.
- Use Pydantic for config validation.
- Use JSON for persistent highscores.
- Use a screen-based architecture for UI flow.
- Use GitHub branches and pull requests for development workflow.
- Include Makefile, tests, documentation, and packaging support for final evaluation.
