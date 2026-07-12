# =============================================================================
# CS661 Group 4 — Data Preprocessing & Sharing Module
# =============================================================================

import pandas as pd
import numpy as np

# Load core datasets
df_all = pd.read_csv('cleaned/cleaned_all_countries.csv')
df_2022 = df_all[df_all['year'] == 2022].copy()

# Add calculated indicators
df_2022['co2_change'] = df_2022['co2_per_capita'] - df_2022['co2_base_2000']
df_bubble_clean = df_2022.dropna(subset=['renewable_share_change', 'co2_change', 'gdp_per_capita', 'decoupling_status_2022'])
df_2022['energy_efficiency'] = 1.0 / df_2022['energy_per_gdp']

# Determine valid country lists
_countries_with_renewables = df_all.groupby('country')['renewables_share_energy'].max()
_valid_countries = _countries_with_renewables[_countries_with_renewables > 0].index

all_countries = sorted(_valid_countries.dropna().tolist())
bubble_countries = sorted(df_bubble_clean['country'].dropna().unique())

# Pre-calculate global mix statistics
ENERGY_SOURCES = ['coal_consumption', 'oil_consumption', 'gas_consumption',
                  'nuclear_consumption', 'hydro_consumption', 'solar_consumption', 'wind_consumption']

df_global = df_all.groupby('year')[ENERGY_SOURCES].apply(lambda x: x.fillna(0).sum()).reset_index()
