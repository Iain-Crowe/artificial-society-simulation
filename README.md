
# Landscape Simulation Project

This project simulates a landscape with agents that move, consume resources, and interact with their environment. The simulation includes a landscape with resources that regrow over time and agents that move based on the available resources.

## Project Structure

- **capacity_models.py**: Contains the functions and models related to resource capacity calculation, including Gaussian distributions.
- **object_models.py**: Defines the core classes used in the simulation, including `Landscape`, `Cell`, and `Agent`.
- **simulate.py**: The main script that runs the simulation. It includes a CLI interface to customize the simulation parameters.

## Usage

You can run the simulation by executing the `simulate.py` script with various command-line arguments to customize the simulation environment.

### CLI Arguments

- `--max_width <int>`: Determines the maximum width for both the landscape and capacity function. Default is 50.
- `--max_height <int>`: Determines the maximum height for the landscape and capacity function. Default is 50.
- `--agents <int>`: Number of agents to simulate. Required.
- `--randomize`: If this flag is set, the landscape will be initialized with randomized arguments for the capacity function.
- `--sleep_time <float>`: Time in seconds to sleep between cycles. Default is 1.0 seconds.

### Example Command

```bash
python simulate.py --max_width 50 --max_height 50 --agents 10 --randomize --sleep_time 1.0
```

This command initializes a 50x50 landscape with 10 agents and randomizes the resource distribution. The simulation updates every second.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Iain-Crowe/artificial-society-simulation.git
    cd artificial-society-simulation
    ```

2. **Run the simulation**:
    ```bash
    python simulate.py
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

- **Author**: Iain Crowe
- **Email**: iainccrowe@gmail.com
