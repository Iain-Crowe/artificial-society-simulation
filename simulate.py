# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

import argparse
import cProfile
import concurrent.futures
import platform
import random
import sys
import time
from typing import List, Optional, Tuple

from components import Agent, Landscape
from components import init_agents
from plot import plot_population_totals

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
        default=500,
        help="Number of cycles to run the simulation for.",
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
        "--agents", "-A", type=int, default=250, help="Number of agents to simulate."
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
        "--display",
        "-V",
        action="store_true",
        help="Display the resource map at each step in simulation.",
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
    else:
        capacity_function_args = {"bounds": (args.max_width, args.max_height)}

    display = args.display

    landscape = Landscape(
        size=(args.max_width, args.max_height),
        **capacity_function_args,
    )

    agents: List[Agent] = init_agents(landscape, args.agents)

    population_totals = []

    print("Initial Map:")
    print_landscape(landscape, len(agents))

    for i in range(1, args.time + 1):
        random.shuffle(agents)

        # Move and reproduce agents
        new_agents = simulate_step(agents)

        # Regrow landscape
        landscape.regrowth()
        landscape.time += 1

        # Update agent list
        agents = new_agents
        population_totals.append(len(agents))

        if display:
            print_landscape(landscape, len(agents), (i, args.time))
            time.sleep(args.sleep_time)
        print(
            f"Current Population at ({i} of {args.time}): {len(agents)}",
            end="\r",
        )

        if len(agents) <= 0:
            print("\nAll agents have died.")
            break

    print_landscape(landscape, len(agents))
    plot_population_totals(population_totals)


def simulate_step(agents: List[Agent]) -> List[Agent]:
    """
    Multithreaded call to update all agents.

    Args:
        agents (List[Agent]): List of currently alive agents.

    Returns:
        List[Agent]: New list of agents after update sequence has completed.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda agent: agent.update(), agents))

    alive_agents: List[Agent] = []
    offspring: List[Agent] = []
    for idx, (alive, child) in enumerate(results):
        if alive:
            alive_agents.append(agents[idx])
        if child:
            offspring.append(child)

    alive_agents.extend(offspring)

    for agent in alive_agents:
        agent.can_reproduce = True

    return alive_agents


def print_landscape(
    landscape: Landscape,
    num_agents: int,
    t: Optional[Tuple[int, int]] = None,
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
    w = landscape.Y * 2

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
            s = "  "
            if isinstance(cell.occupancy, Agent):
                print(f"{AGENT}{s}{RESET}", end="")
            else:
                print(f"{COLOR_MAP[val]}{s}{RESET}", end="")
        print()
    print("=" * w)
    # Print number of agents on map
    print(f"Agents: {num_agents}")
    print("=" * w)

    sys.stdout.flush()


if __name__ == "__main__":
    main()
