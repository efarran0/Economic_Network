# Economic Network

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a simulation framework for modeling and visualizing intertemporal monetary flows in a closed economic network. It is based on agent-level utility optimization and was developed as part of the Data Science Master's program at Universitat Oberta de Catalunya.

---

### Description

This web application simulates a closed economy with two types of agents: **households** and **firms**. Their behavioral rules are derived from the theoretical model detailed in [*Annex B*](https://github.com/efarran0/Economic_Network/blob/main/pdf/memory.pdf) of the associated master's thesis, which outlines the core principles of agent interaction and utility optimization.

The application is divided into two main screens:

* **Setting Screen**: Define initial economic conditions, such as savings, propensities, and stability settings. Launch the simulation via the **Start Simulation** button.
* **Dashboard Screen**: Visualize real-time interaction, including a **heatmap** of inter-agent monetary flows, **interactive sliders** for adjusting parameters, and **time series plots** showing the historical evolution of propensities.

---

### Technology

The project is built using a modern Python stack:

* **Python 3**: The core programming language.

* **NumPy**: For numerical operations.

* **Pandas**: For efficient data manipulation and analysis.

* **Statsmodels**: For statistical modeling and time series analysis.

* **Dash (Plotly)**: For interactive web application and visualizations.

* **Gunicorn**: For deploying the application.

* **Render**: For continuous deployment.
---

### Artificial Intelligence Usage

AI tools were employed as a collaborative partner to support key aspects of the project's development:

* **Code Generation**: For initial code snippets and boilerplate.
* **Performance Optimization**: To identify and improve bottlenecks.
* **Refactoring and Restructuring Assistance**: The core modules (`src/sim.py`, `src/layout.py`, `src/callbacks.py`) were refactored for improved readability, maintainability, and adherence to modern Python best practices.

---

### Cloning and Execution

To get a local copy of the project up and running, follow these steps in your terminal:

**1. Clone the repository**
```bash
git clone https://github.com/efarran0/Economic_Network.git
cd Economic_Network
```

**2. Create and activate a virtual environment (Optional)**
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

Or, alternatively, you can explore the simulation directly through the [Render web application](https://economic-network.onrender.com)

---

## License

This project is licensed under the [**MIT License**](https://github.com/efarran0/Economic_Network/blob/main/LICENSE)
