# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

from __future__ import annotations

import threading
from typing import Any, Callable, List, Tuple, TYPE_CHECKING

from capacity_models import two_peak_guassian

if TYPE_CHECKING:
    from components import Agent


class Cell:
    """
    Simple class to store data on each cell in the landscape.
    """

    def __init__(
        self,
        x: int,
        y: int,
        capacity: float,
        regrowth_rate: float,
    ) -> None:
        """
        Args:
            x (int): x-coord of cell
            y (int): y-coord of cell
            capacity (float): Maximum amount of resources the cell can contain.
            regrowth_rate (float): Rate at which resources replenish.
        """
        self.x = x
        self.y = y

        self.occupancy: Agent = None
        self.capacity = capacity
        self.resource_level: float = self.capacity
        self.regrowth_rate = regrowth_rate

    def __str__(self) -> str:
        return f"Cell({self.x}, {self.y})[occupancy: {self.occupancy}]"


class Landscape:
    """
    Class that manages all the cells and all the agents.
    """

    def __init__(
        self,
        size: Tuple[int, int] = (50, 50),
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
        self.time = 0

        # Lock for synchronizing access to cells and agents.
        self.lock = threading.Lock()

        # Intialize cells
        self.cells: List[List[Cell]] = [
            [
                Cell(
                    x=x,
                    y=y,
                    capacity=capacity_function(x, y, *args, **kwargs),
                    regrowth_rate=regrowth_rate,
                )
                for y in range(self.Y)
            ]
            for x in range(self.X)
        ]

    def regrowth(self) -> None:
        """
        Applies regrowth rate to each cell to replenish resources at each cell up to capacity.
        """
        for X in self.cells:
            for cell in X:
                cell.resource_level = int(
                    min(cell.capacity, cell.resource_level + cell.regrowth_rate)
                )
