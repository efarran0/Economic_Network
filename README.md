# [Economic Network](https://economic-network.onrender.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-rebeccapurple.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

This project provides an interactive simulation and visual analytics dashboard for exploring the evolution of a closed economic network. Based on agent micro-interactions and behavioral inference, it allows users to explore hypothetical economic scenarios, policy interventions, and shock propagation.

The project is developed as part of the Data Science Master's program at [Universitat Oberta de Catalunya](https://www.uoc.edu/es) and corresponds to a Master's Thesis submission on **January 09, 2026**.

---

### Description

This web application simulates a closed economy with two agents: a **household** and a **firm**. Their behavioral rules are derived from the theoretical model detailed in *Annex A* of the associated [Master's thesis](https://github.com/efarran0/Economic_Network/blob/main/pdf/memory.pdf), which outlines the core principles of agent interaction.

The application is divided into two main screens:

* **Setting screen**. Define initial economic conditions, such as savings, propensities, and stability settings. Launch the simulation via the **Start Simulation** button.
* **Dashboard screen**. Visualize real-time interactions, including:
  * **Heatmap** of inter-agent monetary flows
  * **Interactive sliders** for adjusting parameters
  * **Time series plots** showing the historical evolution of propensities
---

### Technology

The project is built using a modern Python stack:

* **Python 3**. The core programming language.
* **NumPy**. For numerical operations.
* **Pandas**. For efficient data manipulation and analysis.
* **Statsmodels**. For statistical modeling and time series analysis.
* **Dash (Plotly)**. For interactive web applications and visualizations.
* **Gunicorn**. For deploying the application.
* **Render**. For continuous deployment.

---

### Artificial Intelligence Usage

AI tools were employed as a collaborative partner to support key aspects of the project's development:

* **Code generation**. For initial code snippets and boilerplate.
* **Performance optimization**. To identify and improve bottlenecks.
* **Refactoring and restructuring assistance**. To improve readability, maintainability, and adherence to modern Python best practices.

---

### Cloning and Execution

* **Quick start:**

    Open the [web application](https://economic-network.onrender.com)

* **Local development:**
  * **0. Prerequisites**
    * Python 3.8 or higher.

  * **1. Clone**
    ```bash
    git clone https://github.com/efarran0/Economic_Network.git
    cd Economic_Network
    python -m venv .venv
    ```

  * **2. Install dependencies and run**

    On Windows:
    ```bash
    .venv\scripts\python.exe -m pip install -r requirements.txt
    .venv\scripts\python.exe -m src.app
    ```
    
    On Linux/macOS:
    ```bash
    ./.venv/bin/python -m pip install -r requirements.txt
    ./.venv/bin/python -m src.app
    ```

---

## License

This project uses a dual-licensing model to ensure proper use and sharing of both software and research material.

The **source code**, located in `/src` and related folders, is licensed under the [**MIT License**](https://github.com/efarran0/Economic_Network/blob/main/LICENSE#L5).

The **academic content**, located in `/pdf`, including all text, figures, and research material, is licensed under the [**CC BY-SA 4.0 License**](https://github.com/efarran0/Economic_Network/blob/main/LICENSE#L30).

---

## Citing

To cite this work, use the following BibTeX reference:

```bibtex
@thesis{FarranMoreno2026,
  author       = {Farran Moreno, Eric},
  title        = {Economic Network Modeling: A Graph-Theoretical Framework Linking Micro-interactions to Macro-dynamics},
  institution  = {Universitat Oberta de Catalunya},
  year         = {2026},
  type         = {Master's Thesis},
  url          = {https://github.com/efarran0/Economic_Network/blob/main/pdf/memory.pdf}
}
```
