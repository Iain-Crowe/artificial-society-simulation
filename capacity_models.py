# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Iain Crowe <iainccrowe@gmail.com>

import math
from typing import Tuple


def two_peak_guassian(
    x: int,
    y: int,
    bounds: Tuple[int, int] = (50, 50),
    psi: float = 4.0,
    peak1: Tuple[float, float] = (0.25, 0.25),
    peak2: Tuple[float, float] = (0.75, 0.75),
    theta_x: float = 0.3,
    theta_y: float = 0.3,
) -> int:
    """
    Calculates the twin-peak guassian distribution at a point rounded to the nearest Integer value.

    Args:
        x (int): X-Coordinate of point.
        y (int): Y-Coordinate of point.
        bounds (Tuple[int, int]): Bounds of the distribution, function will wrap `(x, y)`
        coordinates to stay within bounds. Bounds are in form `(X, Y)`
        psi (float): Coefficent for guassian curve. Defaults to `4.0`.
        peak1 (Tuple[float, float]): Center of peak one described as a pair of percentages of the max bound on x and y. Range is `0.0 <= x, y <= 1.0`. Defaults are `(0.25. 0.25)`.
        peak2 (Tuple[float, float]): Center of peak two described as a pair of percentages of the max bound on x and y. Range is `0.0 <= x, y <= 1.0`. Defaults are `(0.25. 0.25)`.
        theta_x (float): Theta_x for guassian curve. Defaults to `0.3`.
        theta_y (float): Theta_y for guassian curve. Defaults to `0.3`.
    Returns
        int: Value of function at (x, y).
    """
    X = bounds[0]
    Y = bounds[1]

    x = (x + X) % X
    y = (y + Y) % Y

    return round(
        guassian(
            x - peak1[0] * X,
            y - peak1[1] * Y,
            bounds=bounds,
            psi=psi,
            theta_x=theta_x,
            theta_y=theta_y,
        )
        + guassian(
            x - peak2[0] * X,
            y - peak2[1] * Y,
            bounds=bounds,
            psi=psi,
            theta_x=theta_x,
            theta_y=theta_y,
        )
    )


def guassian(
    x: int,
    y: int,
    bounds: Tuple[int, int] = (50, 50),
    psi: float = 4.0,
    theta_x: float = 0.3,
    theta_y: float = 0.3,
) -> float:
    """
    Calculates the guassian distribution at a point.

    Args:
        x (int): X-Coordinate of point.
        y (int): Y-Coordinate of point.
        bounds (Tuple[int, int]): Bounds of the distribution. Bounds are in form `(X, Y)`
        psi (float): Coefficent for guassian curve. Defaults to `4.0`.
        theta_x (float): Theta_x for guassian curve. Defaults to `0.3`.
        theta_y (float): Theta_y for guassian curve. Defaults to `0.3`.
    Returns
        float: Value of function at (x, y).
    """
    X = bounds[0]
    Y = bounds[1]
    theta_x = theta_x * X
    theta_y = theta_y * Y
    return psi * math.exp(-1 * (x / theta_x) ** 2 - (y / theta_y) ** 2)


if __name__ == "__main__":
    # Code to test and visualize the output of the distribution in the terminal.
    # Default values will display within color range, outputs above 4 will break this code...
    import platform

    # Array to map values to color code, f(x, y) equals the index of the color code.
    color_map = [
        "\033[30;100m",
        "\033[30;106m",
        "\033[30;46m",
        "\033[30;104m",
        "\033[30;44m",
    ]

    # Reset color code
    RESET = "\033[0m"

    # For windows...
    if platform.system() == "Windows":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Test twin-peak distribution
    for x in range(50):
        for y in range(50):
            num = two_peak_guassian(x, y)
            print(f"{color_map[num]}{num} {RESET}", end="")
        print()
