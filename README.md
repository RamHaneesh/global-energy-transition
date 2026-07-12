# Global Energy Transition Analytics Dashboard

An interactive, web-based visual analytics dashboard built with Python Dash and Plotly. This platform provides multi-dimensional research, animation, and profile comparisons of the global energy transition, emissions trajectories, and economic decoupling across ~150 countries from 2000 to 2022.

The application leverages academic modeling frameworks (such as the **Tapio Decoupling Elasticity Model**) and modern, responsive UI design to offer policymakers and researchers deep insights into global decarbonization patterns.

---

## 🚀 Key Features

*   **Task 4.1: Global Transition Map**
    *   An animated choropleth world map displaying core transition indicators (Renewable Share %, CO₂ per Capita, and Renewable Growth pp since 2000).
    *   Includes a Play/Pause animation controller showing the global geographic evolution year-by-year.
*   **Task 4.2: Energy Mix Streamgraph**
    *   A stacked streamgraph tracking global energy consumption by source (Coal, Oil, Gas, Nuclear, Hydro, Solar, Wind) from 2000 to 2022.
    *   Supports toggling between absolute volumes (TWh) and percentage shares (%).
*   **Task 4.3: Decoupling Index**
    *   Computes and plots Tapio Decoupling Elasticity index curves ($\beta = \frac{\% \Delta \text{CO}_2}{\% \Delta \text{GDP}}$) starting from 2005 to avoid base-year mathematical spikes.
    *   Visualizes target countries against shaded background bands representing academic classifications: Strong Decoupling, Weak Decoupling, and Coupled.
*   **Task 4.4: Transition Drivers**
    *   A multi-dimensional bubble scatter chart plotting $\Delta$ Renewable Share vs. $\Delta$ CO₂ per Capita.
    *   Bubble sizes reflect GDP per capita. Clicking on any country highlights its complete historical trajectory path since 2000.
*   **Task 4.5: Transition Profiles**
    *   A Parallel Coordinates plot mapping fossil fuel reliance, emissions footprints, electricity access, renewable shares, and growth since 2000.
    *   Includes a selector to filter matching global country lines, or toggle the **Decoupling Medians** mode to compare representative category pathways without outlier distortion.
*   **Task 4.6: Peer Comparison**
    *   A normalized polar radar chart comparing India against its structural peers (China, Brazil, Morocco, Indonesia) and the Global Average across six dimensions.

---

## 📁 Repository Structure

```text
├── app.py                  # Main entry point (layout routing and master callbacks)
├── data_loader.py          # Centralized data loader and preprocessor module
├── config.py               # Visual constants, color palettes, and menu config
├── data_cleaning.py        # Offline data cleaning & preprocessing pipeline
│
├── assets/
│   └── style.css           # Warm amber custom dashboard stylesheet
│
├── cleaned/
│   └── cleaned_all_countries.csv  # Preprocessed transition dataset
│
├── pages/                  # Modular task page divisions
│   ├── __init__.py
│   ├── map_page.py         # Task 4.1 layout & callbacks
│   ├── stream_page.py      # Task 4.2 layout & callbacks
│   ├── index_page.py       # Task 4.3 layout & callbacks
│   ├── bubble_page.py      # Task 4.4 layout & callbacks
│   ├── parallel_page.py    # Task 4.5 layout & callbacks
│   └── radar_page.py       # Task 4.6 layout & callbacks
│
├── requirements.txt        # Python dependency specifications
├── owid-energy-data.csv    # Original Dataset
└── README.md               # Setup and documentation guide
```

---

## 🛠️ Setup & Installation Instructions

### Prerequisites
*   Python 3.8 or higher installed.
*   Git command-line tools installed.

### 1. Clone or Download the Code
If the code is already on your machine, open your terminal (Command Prompt, PowerShell, or Git Bash) in this project folder.

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid package conflicts:

*   **Windows (PowerShell / Command Prompt):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
*   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies
Install all required packages listing in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run Data Preprocessing (Optional)
If you want to re-run the raw data-cleaning routine:
```bash
python data_cleaning.py
```

### 5. Launch the Dashboard
Start the visual analytics dashboard server:
```bash
python app.py
```
After launching, open your browser and navigate to:
👉 **[http://127.0.0.1:8050/](http://127.0.0.1:8050/)**
