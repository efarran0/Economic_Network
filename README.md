# Economic Network Simulator

This project provides a simulation framework for modeling and visualizing intertemporal monetary flows in a closed economic network. It is based on agent-level utility optimization and developed as part of the Data Science Master's program at Universitat Oberta de Catalunya.

## Description

This web application simulates a closed economy with two types of agents: **households** and **firms**. Behavioral rules are derived from the theoretical model detailed in *Annex A* of the associated academic paper.

The application is divided into two main screens:

- **Configuration Screen**:
  - Define initial economic conditions: savings, propensities, and stability settings.
  - Launch the simulation via the **Start Simulation** button.

- **Simulation Screen**:
  - **Heatmap** showing normalized inter-agent monetary flows.
  - **Interactive sliders** to adjust propensity parameters and simulate exogenous changes.
  - **Time series plots** showing the historical evolution of propensities over the last 5 periods.

## Technology

- Python 3  
- NumPy  
- Dash (Plotly)  
- Gunicorn  
- Render (for cloud deployment)

## Artificial Intelligence Usage

AI tools were employed to support:

- Code generation  
- Performance optimization  
- Refactoring and restructuring assistance

## Cloning and Execution

To clone and run the project locally, located in the terminal and follow this steps:

**1. Clone the repository from the remote GitHub source**

git clone https://github.com/efarran0/Economic_Network_Simulator.git
cd Economic_Network_Simulator

**2. Create and activate a virtual environment (Optional)**

python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate

**3. Install required dependencies from the requirements file**

pip install -r requirements.txt

**4. Navigate into the 'src' directory where the main application code resides**

cd src

**5. Execute the application script to launch the visualization**

python app.py

Alternatively, you can explore the simulation directly through the [Render web application](https://economic-network-simulator.onrender.com/)

## License

This project is licensed under MIT License.
