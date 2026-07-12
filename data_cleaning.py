# =============================================================================
# CS661 Group 4 — Data Cleaning & Preprocessing
# Note: If running this script, ensure the raw 'owid-energy-data.csv' is placed
# in the root of this project folder.
# =============================================================================

import pandas as pd
import numpy as np
import os

# Load OWID energy dataset
df = pd.read_csv('owid-energy-data.csv', low_memory=False)

# Filter timeline to 2000-2022
df = df[(df['year'] >= 2000) & (df['year'] <= 2022)]

# Filter for real countries (valid ISO codes and non-aggregates)
mask_countries = df['iso_code'].notna() & ~df['iso_code'].str.startswith('OWID_')
df = df[mask_countries]

# Extract variables required for visual analytics tasks
cols_to_keep = [
    'country', 'iso_code', 'year', 'population', 'gdp',
    'coal_consumption', 'oil_consumption', 'gas_consumption',
    'nuclear_consumption', 'hydro_consumption',
    'solar_consumption', 'wind_consumption',
    'renewables_share_energy', 'renewables_consumption',
    'fossil_share_energy', 'fossil_fuel_consumption',
    'greenhouse_gas_emissions',
    'energy_per_gdp',
    'primary_energy_consumption',
    'per_capita_electricity',
]
df = df[cols_to_keep]
df = df.sort_values(['country', 'year']).reset_index(drop=True)

# Split columns for safe filling (preventing historical baseline distortions)
zero_fill_cols = [
    'coal_consumption', 'oil_consumption', 'gas_consumption',
    'nuclear_consumption', 'hydro_consumption', 'solar_consumption', 'wind_consumption',
    'renewables_share_energy', 'renewables_consumption',
    'primary_energy_consumption', 'per_capita_electricity'
]

nan_fill_cols = [
    'population', 'gdp', 'fossil_share_energy', 'fossil_fuel_consumption',
    'greenhouse_gas_emissions', 'energy_per_gdp'
]

# Apply group-wise forward fill (no back fill applied to protect baseline years)
for col in zero_fill_cols:
    df[col] = df.groupby('country')[col].transform(lambda x: x.ffill().fillna(0))

for col in nan_fill_cols:
    df[col] = df.groupby('country')[col].transform(lambda x: x.ffill())

# Compute derived indicators
df['co2_per_capita'] = (df['greenhouse_gas_emissions'] * 1e6) / df['population']
df['gdp_per_capita'] = df['gdp'] / df['population']

# Baseline index normalization (Year 2000 reference)
base_2000 = df[df['year'] == 2000][['country', 'gdp_per_capita', 'co2_per_capita']].copy()
base_2000 = base_2000.rename(columns={
    'gdp_per_capita': 'gdp_base_2000',
    'co2_per_capita': 'co2_base_2000'
})
df = df.merge(base_2000, on='country', how='left')

df['gdp_index'] = (df['gdp_per_capita'] / df['gdp_base_2000']) * 100
df['co2_index'] = (df['co2_per_capita'] / df['co2_base_2000']) * 100
df['decoupling_gap'] = df['gdp_index'] - df['co2_index']

# Renewable growth since 2000 reference
base_renew = df[df['year'] == 2000][['country', 'renewables_share_energy']].copy()
base_renew = base_renew.rename(columns={'renewables_share_energy': 'renew_share_2000'})
df = df.merge(base_renew, on='country', how='left')
df['renewable_share_change'] = df['renewables_share_energy'] - df['renew_share_2000']

# Tapio Decoupling Elasticity & Classification
df['pct_change_gdp'] = (df['gdp_per_capita'] - df['gdp_base_2000']) / df['gdp_base_2000']
df['pct_change_co2'] = (df['co2_per_capita'] - df['co2_base_2000']) / df['co2_base_2000']

df['tapio_elasticity'] = np.where(
    df['pct_change_gdp'].abs() > 1e-5,
    df['pct_change_co2'] / df['pct_change_gdp'],
    np.nan
)

df['decoupling_status'] = None
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] < 0), 'decoupling_status'] = 'Strong Decoupling'
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] >= 0) & (df['tapio_elasticity'] < 0.8), 'decoupling_status'] = 'Weak Decoupling'
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] >= 0) & (df['tapio_elasticity'] >= 0.8), 'decoupling_status'] = 'Coupled'
df.loc[(df['pct_change_gdp'] <= 0), 'decoupling_status'] = 'Coupled'

# Merge 2022 status snapshot for the bubble scatter chart
status_2022 = df[df['year'] == 2022][['country', 'decoupling_status']].copy()
status_2022 = status_2022.rename(columns={'decoupling_status': 'decoupling_status_2022'})
df = df.merge(status_2022, on='country', how='left')

# Save processed output dataset
os.makedirs('cleaned', exist_ok=True)
df.to_csv('cleaned/cleaned_all_countries.csv', index=False)
print("Saved: cleaned/cleaned_all_countries.csv")
