# Accretion and Compact-Object Collaboration

## Overview
This repository contains simulations for accretion disks of black holes based on initial conditions. Numbers are added onto acc to stress the increasing complexity of the variables added into the functions that define an accreting black hole system.

## Features
- Parsing `.acc` files into structured formats.
- Data analysis and statistical summaries.
- Visualization tools for `.acc` file data.
- Support for batch processing of multiple `.acc` files.

## Getting Started

### Prerequisites
- Python 3.x
- Required libraries: `pandas`, `matplotlib`, `numpy`, etc.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/acc-file-processor.git
   ```
2. Navigate to the repository directory:
   ```bash
   cd acc-file-processor
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
1. Place your `.acc` files in the `data/` directory.
2. Run the main processing script:
   ```bash
   python process_acc_files.py
   ```
3. View the output in the `output/` directory, which includes processed data and visualizations.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For questions or feedback, please contact [your-email@example.com].

## Scripts Overview

This repository contains three main Python scripts for simulating and visualizing accretion disk properties around compact objects like black holes. Each script focuses on a specific aspect of the simulation:

### 1. `acc.py`
This script generates a 2D heatmap of the temperature distribution in an accretion disk based on the mass accretion rate (`Mdot`) and the viscosity parameter (`Alpha`). Key features include:
- **Interactive Heatmap**: Users can click on the heatmap to simulate the accretion disk at specific parameter values.
- **Temperature Visualization**: Displays the temperature of the disk at the selected parameters.
- **Animation**: Simulates the motion of particles in the accretion disk, with their speed and color determined by the temperature.

### 2. `acc1.py`
This script extends the functionality of `acc.py` by introducing:
- **Radial Temperature Profiles**: Simulates temperature variations across the radius of the accretion disk.
- **Interactive Animation**: Visualizes the accretion disk with particles moving at speeds determined by their radial position and temperature.
- **ISCO Calculation**: Computes the innermost stable circular orbit (ISCO) for a Schwarzschild black hole and adjusts the visualization accordingly.
- **Tkinter GUI**: Displays simulation parameters and results in a separate window for better user interaction.

### 3. `acc3d.py`
This script provides a 3D visualization of the temperature distribution in the accretion disk. Key features include:
- **3D Surface Plot**: Plots the temperature as a function of the mass accretion rate (`Mdot`) and the viscosity parameter (`Alpha`).
- **Interactive Visualization**: Allows users to explore the temperature profile in three dimensions.
- **Scientific Insights**: Highlights how changes in accretion parameters affect the disk's temperature.

### Common Features
All scripts share the following core functionalities:
- **Physics-Based Modeling**: Simulations are based on standard accretion disk physics, including the Stefan-Boltzmann law and gravitational energy dissipation.
- **Customizable Parameters**: Users can adjust parameters like mass accretion rate, viscosity, and disk radius to explore different scenarios.
- **Visualization Tools**: Each script includes tools for visualizing the results, either in 2D or 3D.

These scripts are designed to help researchers and students understand the complex dynamics of accretion disks and their dependence on physical parameters.
