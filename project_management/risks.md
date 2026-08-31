# Risks and Mitigation

## Risk 1: Invalid configuration values

**Risk:**  
The evaluator may change `config.json` and enter invalid values.

**Impact:**  
The game may crash or behave unpredictably.

**Mitigation:**  
Use Pydantic validators to clamp invalid values to safe defaults.  
Print clear error messages instead of raising raw tracebacks.

## Risk 2: Maze generation issues

**Risk:**  
Some maze sizes may be too small or unsuitable for the required "42" pattern or Pac-Man gameplay.

**Impact:**  
The maze may be hard to play, invalid, or generate warnings.

**Mitigation:**  
Use safe minimum width and height values.  
Use `perfect=False` for playable mazes with alternative paths.

## Risk 3: Asset loading failure

**Risk:**  
Missing or incorrectly named image/font/music files may crash the game.

**Impact:**  
The game cannot render a screen or start properly.

**Mitigation:**  
Keep all assets inside the repository.  
Use consistent relative paths from the project root.  
Test packaged and local runs.

## Risk 4: Audio device unavailable

**Risk:**  
Some systems may not have an available audio device.

**Impact:**  
Music playback may fail.

**Mitigation:**  
Catch pygame mixer initialization errors and disable music gracefully.

## Risk 5: UI elements overflowing the screen

**Risk:**  
Long text, high scores, or different screen sizes may cause UI elements to overflow.

**Impact:**  
The screen may look broken or drawing may fail.

**Mitigation:**  
Clip drawing safely in `FrameBuffer`.  
Use smaller fonts for HUD hints and fixed positions for UI labels.

## Risk 6: Highscore file corruption

**Risk:**  
The highscore file may be missing, empty, or contain invalid JSON.

**Impact:**  
The highscore screen or name entry may fail.

**Mitigation:**  
Validate highscores using Pydantic.  
Create a new empty leaderboard if the file is missing or invalid.

## Risk 7: Packaging differences

**Risk:**  
The game may work locally but fail when packaged.

**Impact:**  
The submitted build may not run.

**Mitigation:**  
Keep a packaging spec file in the repository.  
Test the packaged build before submission.