# Acceptance Test Plan

## Startup

| Test | Expected Result |
|---|---|
| Run `make install` | Dependencies are installed |
| Run `make run` | Game starts with `config.json` |
| Run `python3 pac-man.py config.json` | Game starts |
| Run without config argument | Clear usage message is shown |
| Run with non-json file | Clear config error is shown |

## Main Menu

| Test | Expected Result |
|---|---|
| Use Up/Down or W/S | Selected menu option changes |
| Press Enter on Start | Game starts |
| Press Enter on Instructions | Instructions screen opens |
| Press Enter on Highscores | Highscores screen opens |
| Press Enter on Settings | Settings screen opens |
| Press Enter on Exit | Game exits |

## Gameplay

| Test | Expected Result |
|---|---|
| Use WASD | Pac-Man moves |
| Use arrow keys | Pac-Man moves |
| Eat regular pacgum | Score increases |
| Eat super pacgum | Ghosts become frightened |
| Touch normal ghost | Life is lost |
| Touch frightened ghost | Ghost is eaten and score increases |
| Eat all pacgums | Level is completed |
| Complete all levels | Victory screen is shown |
| Lose all lives | Game over screen is shown |
| Timer reaches zero | Game over screen is shown |

## Cheat Mode

| Test | Expected Result |
|---|---|
| Press F1 | Invincibility toggles |
| Press F2 | Ghosts stop moving |
| Press F3 | Extra life is added |
| Press F4 | Pac-Man speed increases/decreases |
| Press F5 | Current level is skipped |
| Press any cheat key | Cheat-code legend appears in HUD |

## Pause

| Test | Expected Result |
|---|---|
| Press Escape during gameplay | Pause screen opens |
| Select Resume | Game continues |
| Select Restart | Game restarts |
| Select Main Menu | Main menu opens |
| Select Settings | Settings screen opens |

## Settings

| Test | Expected Result |
|---|---|
| Change wall color | Maze wall color changes |
| Change volume | Music volume changes |
| Press Escape | Settings screen closes |

## Highscores

| Test | Expected Result |
|---|---|
| Finish with eligible score | Name input is shown |
| Enter valid name | Score is saved |
| Open highscores screen | New score appears |
| Enter name longer than 10 characters | Name is limited/rejected |
| Use invalid name characters | Score is not saved |

## Packaging

| Test | Expected Result |
|---|---|
| Build packaged version | Build completes |
| Run packaged version | Game starts |
| Check assets in build | Images, fonts and music are available |