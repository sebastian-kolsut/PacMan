#!/usr/bin/env python3
"""Generate mazes with mazegenerator and validate them with maze_analyzer.

Both packages agree on the wall encoding (bit0=N, 1=E, 2=S, 3=W, one cell
per ``grid[row][col]``) and on entry/exit as ``(row, col)`` tuples, so a
generated board can be handed to :class:`maze_analyzer.Maze` directly.

Usage::

    python3 check_maze_validity.py
    python3 check_maze_validity.py --seeds 1 2 3 --sizes 15 15 --sizes 30 20
    python3 check_maze_validity.py --include-perfect
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Tuple

from mazegenerator import MazeGenerator  # type: ignore[import-untyped]

from maze_analyzer import (
    DEFAULT_MAX_DEAD_ENDS,
    DEFAULT_MIN_LOOPS,
    Maze,
    analyze,
    verdict,
)

DEFAULT_SIZES: List[Tuple[int, int]] = [(10, 10), (20, 20), (35, 20)]
DEFAULT_SEEDS: List[int] = list(range(1, 11))


def to_analyzer_maze(mazegen: MazeGenerator) -> Maze:
    return Maze(mazegen.maze, mazegen.maze_entry, mazegen.maze_exit)


def run_case(width: int, height: int, seed: int, perfect: bool) -> Tuple[bool, str]:
    mazegen = MazeGenerator((width, height), perfect=perfect, seed=seed)
    report = analyze(to_analyzer_maze(mazegen))
    line = verdict(report, DEFAULT_MIN_LOOPS, DEFAULT_MAX_DEAD_ENDS)
    ok = line.startswith("PERFECT maze") if perfect \
        else line.startswith("Pac-Man-USABLE")
    return ok, line


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate mazes with mazegenerator and validate them "
                    "against maze_analyzer's default thresholds.",
    )
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
        help="seeds to generate (default: 1-10)",
    )
    parser.add_argument(
        "--sizes", type=int, nargs=2, action="append", metavar=("WIDTH", "HEIGHT"),
        dest="sizes",
        help="width height pair to test (repeatable; default: 10x10, 20x20, "
             "35x20)",
    )
    parser.add_argument(
        "--include-perfect", action="store_true",
        help="also generate perfect=True mazes and expect the PERFECT verdict",
    )
    args = parser.parse_args(argv)
    if not args.sizes:
        args.sizes = DEFAULT_SIZES
    return args


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    modes = [False, True] if args.include_perfect else [False]
    total = failures = 0
    for width, height in args.sizes:
        for seed in args.seeds:
            for perfect in modes:
                total += 1
                ok, line = run_case(width, height, seed, perfect)
                status = "PASS" if ok else "FAIL"
                mode = "perfect" if perfect else "imperfect"
                print(f"[{status}] {width}x{height} seed={seed} ({mode}): {line}")
                failures += not ok
    print(f"\n{total - failures}/{total} maze(s) passed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
