# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

from typing import List

import matplotlib.pyplot as plt


def plot_population_totals(population_totals: List[int]) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(population_totals, marker="o", linestyle="-", color="b")
    plt.title("Population Totals Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Population")
    plt.show()
