# =============================================================================
# CS661 Group 4 — Layout & Aesthetic Constants Configuration
# =============================================================================

import plotly.express as px
from data_loader import df_all

# Default country selections for line charts & drop-downs
DEFAULT_COUNTRIES = [
    'Denmark', 'France', 'United States', 'Brazil',
    'Morocco', 'China', 'India', 'Indonesia'
]

# Standard hex code mappings for consistent country colors
CUSTOM_COLORS = {
    'Denmark':        '#2ca02c',
    'France':         '#1f77b4',
    'United States':  '#9467bd',
    'Brazil':         '#bcbd22',
    'Morocco':        '#17becf',
    'China':          '#d62728',
    'India':          '#ff7f0e',
    'Indonesia':      '#7B3FA0'
}

COLOR_PALETTE = px.colors.qualitative.Dark24

# Choropleth Map Metrics definitions (Task 4.1)
MAP_METRICS = {
    'renewables_share_energy': {
        'label': '% Renewable Share',
        'color_scale': 'Greens',
        'unit': '%',
        'range': [df_all['renewables_share_energy'].min(), df_all['renewables_share_energy'].max()]
    },
    'co2_per_capita': {
        'label': 'CO₂ per Capita',
        'color_scale': 'Reds',
        'unit': 'tonnes',
        'range': [df_all['co2_per_capita'].min(), df_all['co2_per_capita'].max()]
    }
}

# Energy source categories for Streamgraph (Task 4.2)
ENERGY_SOURCES = ['coal_consumption', 'oil_consumption', 'gas_consumption',
                  'nuclear_consumption', 'hydro_consumption', 'solar_consumption', 'wind_consumption']

SOURCE_LABELS = {
    'coal_consumption': 'Coal', 'oil_consumption': 'Oil', 'gas_consumption': 'Gas',
    'nuclear_consumption': 'Nuclear', 'hydro_consumption': 'Hydro',
    'solar_consumption': 'Solar', 'wind_consumption': 'Wind'
}

SOURCE_COLORS = {
    'coal_consumption': '#3d2b1f', 'oil_consumption': '#8B4513',
    'gas_consumption': '#CD853F', 'nuclear_consumption': '#9370DB',
    'hydro_consumption': '#4169E1', 'solar_consumption': '#FFD700',
    'wind_consumption': '#00CED1'
}

# Sidebar Navigation Pages configuration
PAGES = [
    {
        'id': 'page-map',
        'nav_id': 'nav-map',
        'icon': '🗺️',
        'label': 'Global Transition Map',
        'short': 'Task 4.1',
        'desc': 'A world choropleth showing renewable share, change since 2000, or CO₂ per capita — animated from 2000 to 2022.'
    },
    {
        'id': 'page-stream',
        'nav_id': 'nav-stream',
        'icon': '🌊',
        'label': 'Energy Mix',
        'short': 'Task 4.2',
        'desc': 'Global energy consumption by source from 2000–2022. Watch renewables grow while fossil fuels hold their ground.'
    },
    {
        'id': 'page-decouple',
        'nav_id': 'nav-decouple',
        'icon': '📉',
        'label': 'Decoupling Index',
        'short': 'Task 4.3',
        'desc': 'GDP index vs. CO₂ index — using the Tapio Elasticity model to distinguish strong, weak, and coupled states.'
    },
    {
        'id': 'page-bubble',
        'nav_id': 'nav-bubble',
        'icon': '🔵',
        'label': 'Transition Drivers',
        'short': 'Task 4.4',
        'desc': 'Bubble chart across ~150 countries: does growing renewable share actually reduce CO₂? The answer is complicated.'
    },
    {
        'id': 'page-parallel',
        'nav_id': 'nav-parallel',
        'icon': '⚡',
        'label': 'Transition Profiles',
        'short': 'Task 4.5',
        'desc': 'Parallel coordinates across 5 dimensions — three distinct transition archetypes emerge when you look at all axes together.'
    },
    {
        'id': 'page-radar',
        'nav_id': 'nav-radar',
        'icon': '🎯',
        'label': 'Peer Comparison',
        'short': 'Task 4.6',
        'desc': 'Radar chart comparing India against its true peers — China, Brazil, Morocco, Indonesia — across 6 energy dimensions.'
    },
]
