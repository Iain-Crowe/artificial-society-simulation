
# Landscape Simulation Project

This project simulates a landscape with agents that move, consume resources, and reproduce. The simulation includes a landscape with resources that regrow over time and agents that move based on the available resources.

## Project Structure

- **capacity_models.py**: Contains the functions and models related to resource capacity calculation, including Gaussian distributions.
- **components**: Module containing the core classes used in the simulation, including `Landscape`, `Cell`, and `Agent`.
    - **landscape.py**: Contains classes for `Landscape` and `Cell`.
    - **agent.py** Contains the class for `Agent` as well as a function to initialize a number of Agents.
- **simulate.py**: The main script that runs the simulation. It includes a CLI interface to customize the simulation parameters.

## Usage

You can run the simulation by executing the `simulate.py` script with various command-line arguments to customize the simulation environment.

### CLI Arguments

- `--time <int>` or `-T`: Number of cycles to run the simulation for. Default is 500.
- `--max_width <int>` or `-X`: Determines the maximum width for both the landscape and capacity function. Default is 50.
- `--max_height <int>` or `-Y`: Determines the maximum height for the landscape and capacity function. Default is 50.
- `--agents <int>` or `-A`: Number of agents to simulate. Default is 250.
- `--randomize` or `-R`: If this flag is set, the landscape will be initialized with randomized arguments for the capacity function.
- `--sleep_time <float>` or `-S`: Time in seconds to sleep between cycles. Default is 1.0 seconds.
- `--display` or `-D`: Display the resource map at each step in simulation. 

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

2. **Setup virtual environment and install dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate    # 'venv\Scripts\activate' on Windows
    pip install -r requirements
    ```

3. **Run the simulation**:
    ```bash
    python simulate.py <args>
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

- **Author**: Iain Crowe
- **Email**: iainccrowe@gmail.com
