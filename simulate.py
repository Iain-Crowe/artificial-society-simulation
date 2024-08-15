# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

import argparse
import platform
import random
import sys
import time
from typing import Optional, Tuple

from object_models import Landscape

# Color map for landscape printing
# This map supports values up to 9, which should be good for any map up to
# 50x50, I haven't tested anything higher. There is likely a more scalable way
# of doing this but for my purposes it wasn't necessary.
COLOR_MAP = [
    "\033[30;100m",
    "\033[30;106m",
    "\033[30;46m",
    "\033[30;104m",
    "\033[30;44m",
    "\033[30;45m",
    "\033[30;105m",
    "\033[30;101m",
    "\033[30;41m",
    "\033[30;40m",
]

# Other helpful codes for printing
RESET = "\033[0m"
AGENT = "\033[30;43m"
CLEAR_SCREEN = "\033[2J"
CURSOR_UP_LEFT = "\033[H"

# For windows...
if platform.system() == "Windows":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def main():
    parser = argparse.ArgumentParser(description="Simulate a landscape with agents.")
    parser.add_argument(
        "--time",
        "-T",
        type=int,
        default=10,
        help="Number of cycles to run the simulation at.",
    )
    parser.add_argument(
        "--max_width",
        "-X",
        type=int,
        default=50,
        help="Determines the max width for both the landscape and capacity function.",
    )
    parser.add_argument(
        "--max_height",
        "-Y",
        type=int,
        default=50,
        help="Determines the max height for both the landscape and capacity function.",
    )
    parser.add_argument(
        "--agents", "-A", type=int, default=50, help="Number of agents to simulate."
    )
    parser.add_argument(
        "--randomize",
        "-R",
        action="store_true",
        help="Initialize the landscape with randomized arguments for the capacity function.",
    )
    parser.add_argument(
        "--sleep_time",
        "-S",
        type=float,
        default=1.0,
        help="Time between updates in simulation, for readability purposes.",
    )
    parser.add_argument(
        "--display_values",
        "-V",
        action="store_true",
        help="Display the resource levels on each tile when printing the landscape map.",
    )

    args = parser.parse_args()

    # Set up landscape and agents
    capacity_function_args = {}
    if args.randomize:
        capacity_function_args = {
            "bounds": (args.max_width, args.max_height),
            "psi": random.uniform(1.0, 5.0),
            "peak1": (random.uniform(0.1, 0.9), random.uniform(0.1, 0.9)),
            "peak2": (random.uniform(0.1, 0.9), random.uniform(0.1, 0.9)),
            "theta_x": random.uniform(0.1, 0.5),
            "theta_y": random.uniform(0.1, 0.5),
        }

    display = args.display_values

    landscape = Landscape(
        size=(args.max_width, args.max_height),
        num_agents=args.agents,
        **capacity_function_args,
    )

    print("Initial Map:")
    print_landscape(landscape, display)

    for t in range(args.time):
        landscape.move_agents()
        landscape.regrowth()
        print_landscape(landscape, display, (t + 1, args.time))

        if len(landscape.agents) == 0:
            print(f"\nAll agents died at time: {t}")

        time.sleep(args.sleep_time)

    print(f"\nSurvivors: {len(landscape.agents)} out of {landscape.starting_agents}")


def print_landscape(
    landscape: Landscape, display_tag: bool, t: Optional[Tuple[int, int]] = None
) -> None:
    """
    Prints the current state of the landscape.

    Args:
        landscape (Landscape): A reference to the landscape object.
        display_tag (bool): Tag to toggle displaying the resource values at each cell.
        t (Optional[Tuple[int, int]]): Optional argument used to pass which generation the landscape is on. Format is (Current, Total).
    """
    print(CLEAR_SCREEN, end="")
    print(CURSOR_UP_LEFT, end="")

    string = f" {t[0]}/{t[1]}" if t else ""
    w = landscape.X * 2

    print("=" * w)
    print(f"\033[97;1mLandscape Map{string}:{RESET}")
    print("=" * w)
    # Print the key
    print("Key:")
    for i, color in enumerate(COLOR_MAP):
        print(f"{i} = {color[:-1]};4m  {RESET}", end="\n" if (i + 1) % 4 == 0 else "; ")
    print(f"Agent = {AGENT[:-1]};4m  {RESET}")
    print("=" * w)
    # Print the map
    for X in landscape.cells:
        for cell in X:
            val = cell.resource_level
            s = val if display_tag else " "
            if cell.occupancy:
                print(f"{AGENT}{s} {RESET}", end="")
            else:

                print(f"{COLOR_MAP[val]}{s} {RESET}", end="")
        print()
    print("=" * w)
    # Print number of agents on map
    print(f"Agents: {len(landscape.agents)}")
    print("=" * w)

    sys.stdout.flush()


if __name__ == "__main__":
    main()
