# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

from __future__ import annotations

from enum import Enum
import random
from typing import List, Optional, Tuple

from components.landscape import Cell, Landscape


class Sex(Enum):
    MALE = False
    FEMALE = True


class Agent:
    curr_id = 0

    def __init__(
        self,
        x: int,
        y: int,
        landscape: Landscape,
        fov: int = None,
        metabolism: float = None,
        endowment: float = None,
        lifespan: float = None,
    ) -> None:
        """
        Args:
            x (int): x-coord for agent
            y (int): y-coord for agent
            landscape (Landscape): ref to parent landscape class
            fov (int, optional): How far agent can see. Defaults to `x ∈ Z and x ∈ [1, 6]`.
            metabolism (float, optional): Rate at which agent consumes resources. Defaults to `x ∈ R and x ∈ [1.0, 4.0]`.
            endowment (float, optional): Intial amount of resource agent starts with. Defaults `x ∈ R and x ∈ [50.0, 100.0]`.
            lifespan (float, optional): Length of agent's life. Defaults to `x ∈ R and x ∈ [60.0, 100.0]`.
        """
        # Identifier and parent ref
        self.id = Agent.next_id()
        self.parent = landscape

        # Position
        self.x = x
        self.y = y

        # Survival factors
        self.fov = fov if fov is not None else random.randint(1, 6)
        self.endowment = (
            endowment if endowment is not None else random.uniform(50.0, 100.0)
        )
        self.wealth = self.endowment
        self.metabolism = (
            metabolism if metabolism is not None else random.uniform(1.0, 4.0)
        )
        self.lifespan = (
            lifespan if lifespan is not None else random.uniform(60.0, 100.0)
        )
        self.alive = True

        # Reproduction factors
        self.can_reproduce = True
        self.time_of_birth = landscape.time
        self.sex = random.choice(
            list(Sex)
        )  # Enum for sex either MALE = False or Female = True
        self._fertiliy_begin = random.uniform(12.0, 15.0)
        self._fertiliy_end = (
            random.uniform(40.0, 50.0) if self.sex else random.uniform(50.0, 60.0)
        )
        self.gestation_period = 0

    def __str__(self) -> str:
        return f"Agent[id:{id}]"

    @classmethod
    def next_id(cls) -> int:
        """
        Used to give a unique id to each agent. Counts sequentially from 0

        Returns:
            int: Next id in sequence.
        """
        next_id = cls.curr_id
        cls.curr_id += 1
        return next_id

    @property
    def age(self) -> float:
        """
        Returns:
            float: Age of agent, landscape global time minus time of birth.
        """
        return self.parent.time - self.time_of_birth

    @property
    def fertile(self) -> bool:
        """
        Returns:
            bool: True if fertile, False if not. Based on age and amount of wealth.
        """
        return (
            self._fertiliy_begin <= self.age <= self._fertiliy_end
            and self.wealth >= self.endowment
        )

    @property
    def empty_neighbors(self) -> Optional[List[Cell]]:
        """
        Returns:
            Optional[List[Cell]]: List of cells within fov that are empty, None if no cells are empty.
        """
        neighbors = self._von_neumann_neighborhood()
        return [cell for cell in neighbors if cell.occupancy is None]

    def update(self) -> Tuple[bool, Optional[Agent]]:
        """
        Preforms a single tick of agent's lifecycle: consume, move, reproduce. Consume is combined
        with move.

        Returns:
            Tuple[bool, Optional[Agent]]: bool indicates survival of the agent, Optional[Agent] passes back any offspring made by the agent.
        """
        # Age check, kill agent if past lifespan.
        if self.age > self.lifespan:
            current_cell = self.parent.cells[self.x][self.y]
            current_cell.occupancy = None
            self.alive = False
            return (self.alive, None)

        if not self.move():
            return (self.alive, None)
        offspring = self.reproduce()

        return (self.alive, offspring)

    def move(self) -> bool:
        """
        Moves agent to cell with the most resources within its fov. Ties are broken randomly and
        the fov is calculated using `_von_neumann_neighborhood()`.

        Returns:
            bool: `True` if agent is alive, `False` otherwise
        """
        with self.parent.lock:
            current_cell = self.parent.cells[self.x][self.y]

            # Calculate wealth for agent and resource level at cell
            self.wealth = max(
                0, self.wealth + current_cell.resource_level - self.metabolism
            )
            current_cell.resource_level = 0

            # Calculate if agent dies
            if self.wealth <= 0:
                self.alive = False
                current_cell.occupancy = None
                return self.alive

            # Get cells to check
            check_cells = self.empty_neighbors

            # Random tie breaks implemented by shuffling list of cells
            random.shuffle(check_cells)

            # Grab cell with most resources
            best_cell = max(
                (cell for cell in check_cells if not cell.occupancy),
                key=lambda c: c.resource_level,
                default=None,
            )

            # If best cell is found move to it, theoritcally should never be None *shrug*.
            if best_cell:
                self._move_cell_to(best_cell)

        return self.alive

    def _move_cell_to(self, cell: Cell) -> None:
        """
        Helper function for moving agent to specified cell. Mostly here to declutter `move()`.

        Args:
            cell (Cell): Reference to cell that agent will move to.
        """
        # Get ref to current cell and remove agent from its occupancy
        current = self.parent.cells[self.x][self.y]
        current.occupancy = None

        # Move agent to new cell
        self.x, self.y = cell.x, cell.y
        cell.occupancy = self

    def reproduce(self) -> Optional[Agent]:
        """
        Handles the reproduction logic for the agent. The general idea is to find 4 candidates
        within the agent's fov that are fertile and of opposite sex. Then the agent will choose
        the one with the most wealth. If either agent has a free space in their fov, they will spawn
        a new agent with their endowment attributes avveraged.

        Returns:
            Optional[Agent]: If reproduction is successful the offspring is returned, otherwise None.
        """
        if not self.fertile:
            return None

        with self.parent.lock:
            # Get von Neumann neighborhood with radius self.fov
            neighbor_cells = self._von_neumann_neighborhood()

            # Identify 4 possible candidates
            candidates: List[Agent, float] = []
            for cell in neighbor_cells:
                if (
                    cell.occupancy
                    and cell.occupancy.sex != self.sex
                    and cell.occupancy.fertile
                ):
                    candidates.append(cell.occupancy)
                    if len(candidates) >= 4:
                        break

            # If none are found, reproduction attept failed return None
            if not candidates:
                return None

            # Cache the empty cells for current agent
            own_empty_neighbors = set(self.empty_neighbors)

            # Pick partner with most wealth where a empty cell exists in either agent's
            # von Neumann neighborhood
            partner = None
            best_wealth = -float("inf")
            for candidate in candidates:
                candidate_empty_neighbors = set(candidate.empty_neighbors)
                union_empty_cells = own_empty_neighbors.union(candidate_empty_neighbors)
                if union_empty_cells and candidate.wealth > best_wealth:
                    best_wealth = candidate.wealth
                    partner = candidate

            # If suitable partner is found, create new agent.
            if partner and union_empty_cells:
                offspring_pos = random.choice(list(union_empty_cells))
                offspring = Agent(
                    x=offspring_pos.x,
                    y=offspring_pos.y,
                    landscape=self.parent,
                    endowment=(self.endowment + partner.endowment) / 2,
                )

                offspring_pos.occupancy = offspring
                self.can_reproduce = False

                return offspring

        return None

    def _von_neumann_neighborhood(self) -> List[Cell]:
        """
        Helper function to calculate possible reproduction cells.

        Returns:
            List[Cell]: List of possible reproduction cells.
        """
        neighbors = set()

        for dx in range(-self.fov, self.fov + 1):
            for dy in range(-self.fov + abs(dx), self.fov - abs(dx) + 1):
                nx, ny = self.x + dx, self.y + dy
                bounded_x = max(0, min(nx, self.parent.X - 1))
                bounded_y = max(0, min(ny, self.parent.Y - 1))
                neighbors.add(self.parent.cells[bounded_x][bounded_y])

        return list(neighbors)


def init_agents(landscape: Landscape, num_agents: int) -> List[Agent]:
    """
    Initializes `num_agents` agents before starting the simulation.

    Args:
        landscape (Landscape): Reference to parent landscape class for all agents.
        num_agents (int): Number of agents to initialize. Constraints `0 < num_agents <= X * Y`
    Returns:
        List[Agent]: List of all newly intialized agents.
    """
    X = landscape.X
    Y = landscape.Y
    cells = landscape.cells

    agents = []

    num_agents = min(num_agents, X * Y)

    while len(agents) < num_agents:
        x = random.randint(0, X - 1)
        y = random.randint(0, Y - 1)

        if not cells[x][y].occupancy:
            agent = Agent(x=x, y=y, landscape=landscape)
            cells[x][y].occupancy = agent
            agents.append(agent)

    return agents
