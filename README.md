# [Economic Network](https://economic-network.onrender.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-rebeccapurple.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

This project provides a simulation framework for modeling and visualizing the evolution of a closed economic network. It is based on agent micro-interactions and was developed as part of the Data Science Master's program at [Universitat Oberta de Catalunya](https://www.uoc.edu/es).

---

### Description

This web application simulates a closed economy with two agents: a **household** and a **firm**. Their behavioral rules are derived from the theoretical model detailed in *Annex A* of the associated [master's thesis](https://github.com/efarran0/Economic_Network/blob/main/pdf/memory.pdf), which outlines the core principles of agent interaction.

The application is divided into two main screens:

* **Setting Screen**: Define initial economic conditions, such as savings, propensities, and stability settings. Launch the simulation via the **Start Simulation** button.
* **Dashboard Screen**: Visualize real-time interactions, including a **heatmap** of inter-agent monetary flows, **interactive sliders** for adjusting parameters, and **time series plots** showing the historical evolution of propensities.

---

### Technology

The project is built using a modern Python stack:

* **Python 3**: The core programming language.
* **NumPy**: For numerical operations.
* **Pandas**: For efficient data manipulation and analysis.
* **Statsmodels**: For statistical modeling and time series analysis.
* **Dash (Plotly)**: For interactive web applications and visualizations.
* **Gunicorn**: For deploying the application.
* **Render**: For continuous deployment.

---

### Artificial Intelligence Usage

AI tools were employed as a collaborative partner to support key aspects of the project's development:

* **Code Generation**: For initial code snippets and boilerplate.
* **Performance Optimization**: To identify and improve bottlenecks.
* **Refactoring and Restructuring Assistance**: To improve readability, maintainability, and adherence to modern Python best practices.

---

### Cloning and Execution

To get a local copy of the project up and running, follow these steps in your terminal:

**1. Clone the repository**
```bash
git clone https://github.com/efarran0/Economic_Network.git
cd Economic_Network
```

**2. Create and activate a virtual environment (optional)**
```bash
python -m venv .venv
```

On Windows:
```bash
./.venv/Scripts/activate
```

On Linux/macOS:
```bash
source ./.venv/bin/activate
```

**3. Install required dependencies from the requirements file**
```bash
pip install -r requirements.txt
```

**4. Execute the application script to launch the visualization**
```bash
python -m src.app
```

Or, alternatively, you can explore the simulation directly through the [Render web application](https://economic-network.onrender.com).

---

## License

This project uses a dual-licensing model to ensure proper use and sharing of both software and research material.

The **source code**, located in `/src` and related folders, is licensed under the [**MIT License**](https://github.com/efarran0/Economic_Network/blob/main/LICENSE#L5).

The **academic content**, located in `/pdf`, including all text, figures, and research material, is licensed under the [**CC BY-SA 4.0 License**](https://github.com/efarran0/Economic_Network/blob/main/LICENSE#L30).

---

## Citing

If you use this work in your research, please cite the associated master's thesis:

```bibtex
@mastersthesis{FarranMoreno2025,
  author = {Eric Farran Moreno},
  title = {Economic Network Modeling: A Graph-Theoretical Framework Linking Micro-interactions to Macro-dynamics},
  school = {Universitat Oberta de Catalunya},
  year = {2025},
  url = {https://github.com/efarran0/Economic_Network/blob/main/pdf/memory.pdf}
}
```
