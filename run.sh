#!/bin/bash
# Launcher for the packaged PacMan build (dist/). Lets players just
# double-click/run this instead of hunting for the executable and
# remembering the required config.json argument.
cd "$(dirname "$0")"
./PacMan/PacMan PacMan/config.json
