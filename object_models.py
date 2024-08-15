# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

from __future__ import annotations

import random
from typing import Any, Callable, List, Tuple

from capacity_models import two_peak_guassian


class Cell:
    """
    Simple class to store data on each cell in the landscape.
    """

    def __init__(
        self,
        capacity: float,
        regrowth_rate: float,
        occupancy: bool = False,
    ) -> None:
        """
        Args:
            capacity (float): Maximum amount of resources the cell can contain.
            regrowth_rate (float): Rate at which resources replenish.
            occupancy (bool): Indicates if an agent is occupying the cell. Default `False`.
        """
        self.occupancy = occupancy
        self.capacity = capacity
        self.resource_level: float = self.capacity
        self.regrowth_rate = regrowth_rate


class Agent:
    """
    Class responsible for handling agent interactions on the landscape.
    """

    def __init__(
        self,
        id: int,
        x: int,
        y: int,
        landscape: Landscape,
        wealth: float = 0.0,
        meta_rate: float = 1.0,
        vision: int = 3,
    ) -> None:
        """
        Args:
            id (int): Unique identifier, assigned sequentially.
            x (int): X-coordinate on landscape.
            y (int): Y-coordinate on landscape.
            landscape (Landscape): Reference to parent Landscape instance.
            wealth (float): Amount of 'resource' agent has.
            meta_rate (float): Metabolic rate, amount of 'resource' agent consumes per round.
            vision (int): Controls how far the agent can see/move.
        """
        self.id = id
        self.x = x
        self.y = y
        self.wealth = wealth
        self.meta_rate = meta_rate
        self.vision = vision
        self._parent = landscape
        self.alive = True

    def move(self) -> bool:
        """
        Moves the agent based on several constraints:
        - Agent cannot move off the map
        - Agent can only move up, down, left, or right
        - Agent can only move `self.vision` number of cells
        - Agent will check each possible cell
        - Agent cannot move to an already occupied cell
        - Agent will choose the cell with the most resources (ties are broken randomly)
        - Agent will take all resources on the new cell
        - Wealth is calculated using `max(0, wealth + cell.resource_level - meta_rate)`
        - If weath falls below 0, agent 'dies'.

        Kind of a complicated method, should likely be broken up into smaller methods...\
        
        Returns:
            bool: `True` if agent is alive, `False` otherwise
        """
        check_cells: List[Tuple[int, int]] = []

        for i in range(self.x - self.vision, self.x + self.vision + 1):
            check_cells.append((i, self.y))
        for i in range(self.y - self.vision, self.y + self.vision + 1):
            check_cells.append((self.x, i))

        X = self._parent.X
        Y = self._parent.Y
        check_cells = [(x, y) for x, y in check_cells if 0 <= x < X and 0 <= y < Y]

        random.shuffle(check_cells)

        best_cell = None
        for _ in check_cells:
            x, y = _
            cell = self._parent.cells[x][y]

            if cell.occupancy:
                continue

            if best_cell is None:
                best_cell = (x, y)
                continue

            comp = self._parent.cells[best_cell[0]][best_cell[1]]

            if cell.resource_level > comp.resource_level:
                best_cell = (x, y)

        if best_cell is not None:
            current_cell = self._parent.cells[self.x][self.y]
            current_cell.occupancy = False

            x, y = best_cell
            self.x = x
            self.y = y

            new_cell = self._parent.cells[x][y]
            new_cell.occupancy = True
            self.wealth = max(0, self.wealth + cell.resource_level - self.meta_rate)
            new_cell.resource_level = 0

            if self.wealth <= 0:
                self.alive = False
                new_cell.occupancy = False

        return self.alive


class Landscape:
    """
    Class that manages all the cells and all the agents.
    """

    def __init__(
        self,
        size: Tuple[int, int] = (50, 50),
        num_agents: int = 10,
        regrowth_rate: float = 1.0,
        capacity_function: Callable[..., int] = two_peak_guassian,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            size (Tuple[int, int]): Size of landscape in form `(max_x, max_y)`. Default `(50, 50)`
            num_agents (int): Number of agents to attempt to place, may not place full amount due to collisions. Default is `10`
            regrowth_rate (float): Rate at which cells replenish resources. Default is `1.0`.
            capacity_function (Callable[..., int]): Function used to calculate capacity at each cell. Should be a function `f(x, y)` that returns an `int`. Default is `two_peak_guassian()`.
            *args (Any): Args for capacity function.
            **kwargs (Any): Keyword args for capacity function.
        """
        self.X, self.Y = size

        # Intialize cells
        self.cells: List[List[Cell]] = [
            [
                Cell(
                    capacity=capacity_function(x, y, *args, **kwargs),
                    regrowth_rate=regrowth_rate,
                )
                for y in range(self.Y)
            ]
            for x in range(self.X)
        ]

        # Initialize agents in landscape
        self.agents: List[Agent] = []
        for i in range(num_agents):
            x = random.randint(0, self.X - 1)
            y = random.randint(0, self.Y - 1)
            if not self.cells[x][y].occupancy:
                self.cells[x][y].occupancy = True
                self.agents.append(
                    Agent(
                        i + 1,
                        x,
                        y,
                        self,
                        wealth=random.uniform(5.0, 25.0),
                        meta_rate=random.uniform(1.0, 4.0),
                        vision=random.randint(1, 6),
                    )
                )
        self.starting_agents = len(self.agents)

    def regrowth(self) -> None:
        """
        Applies regrowth rate to each cell to replenish resources at each cell up to capacity.
        """
        for X in self.cells:
            for cell in X:
                cell.resource_level = int(
                    min(cell.capacity, cell.resource_level + cell.regrowth_rate)
                )

    def move_agents(self) -> None:
        """
        Shuffles agents order and then moves them.
        """
        random.shuffle(self.agents)
        self.agents = [agent for agent in self.agents if agent.move()]
