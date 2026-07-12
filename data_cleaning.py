# =============================================================================
# CS661 Group 4 — Data Cleaning & Preprocessing
# Dataset: OWID Energy Dataset (owid-energy-data.csv)
# Output:  cleaned/ folder with 3 ready-to-use CSV files
# =============================================================================

import pandas as pd
import os

# =============================================================================
# STEP 1: LOAD THE RAW DATA
# =============================================================================
# pd.read_csv() reads the CSV file into a DataFrame (like a table in Python).
# Low_memory=False avoids a warning caused by mixed types in large files.

df = pd.read_csv('owid-energy-data.csv', low_memory=False)

print("--- STEP 1: Raw Data Loaded ---")
print(f"Shape: {df.shape}")           # (23377, 130)
print(f"Year range: {df['year'].min()} - {df['year'].max()}")  # 1900 - 2025
print()


# =============================================================================
# STEP 2: FILTER TO YEARS 2000–2022
# =============================================================================
# We only need this time window for the project.
# Data before 2000 is sparse for renewables; after 2022 is out of scope.
# The & operator combines two conditions — both must be True to keep a row.

df = df[(df['year'] >= 2000) & (df['year'] <= 2022)]

print("--- STEP 2: Filtered to 2000–2022 ---")
print(f"Shape: {df.shape}")
print()


# =============================================================================
# STEP 3: REMOVE REGIONAL AGGREGATES (keep only real countries)
# =============================================================================
# The dataset includes rows for "Africa", "Asia", "ASEAN (Ember)" etc.
# These are NOT real countries — they are regional totals added by OWID.
#
# How to detect them:
#   - Real countries have a proper 3-letter ISO code: IND, USA, DNK, etc.
#   - Aggregates either have NaN in iso_code OR start with "OWID_"
#     (e.g., "OWID_AFR" for Africa, "OWID_ASI" for Asia)
#
# notna()         → keeps rows where iso_code is not NaN
# ~str.startswith → the ~ means NOT; removes rows whose iso_code starts with OWID_

mask_real_countries = (
    df['iso_code'].notna() &
    ~df['iso_code'].str.startswith('OWID_')
)
df = df[mask_real_countries]

print("--- STEP 3: Removed Regional Aggregates ---")
print(f"Shape: {df.shape}")
print(f"Unique real countries: {df['country'].nunique()}")
print()


# =============================================================================
# STEP 4: SELECT ONLY THE COLUMNS WE NEED
# =============================================================================
# The dataset has 130 columns but we only need ~20 for our 6 tasks.
# Keeping fewer columns makes everything faster and cleaner.
#
# What each column is used for:
#   country, iso_code, year, population → needed in every task
#   gdp                                 → Decoupling (Task 4.3), Bubble (4.4), Radar (4.6)
#   coal/oil/gas/nuclear/hydro/solar/wind_consumption → Streamgraph (Task 4.2)
#   renewables_share_energy             → Choropleth (4.1), Parallel Coords (4.5), Radar (4.6)
#   renewables_consumption              → Streamgraph (4.2)
#   fossil_share_energy                 → Parallel Coords (4.5), Radar (4.6)
#   fossil_fuel_consumption             → Streamgraph (4.2)
#   greenhouse_gas_emissions            → all CO₂-related tasks
#   energy_per_gdp                      → Energy Efficiency axis in Radar (4.6)
#   primary_energy_consumption          → Streamgraph (4.2) total reference
#   per_capita_electricity              → general reference

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

print("--- STEP 4: Selected Relevant Columns ---")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print()


# =============================================================================
# STEP 5: HANDLE MISSING VALUES (Forward Fill + Back Fill)
# =============================================================================
# Many cells are NaN (missing). The project proposal says to use forward-fill.
#
# Forward-fill (ffill):
#   If a country is missing data for year 2005, use the value from 2004.
#   This is sensible for slowly-changing indicators like renewable share %.
#
# Back-fill (bfill):
#   Applied after ffill to catch cases where the FIRST year(s) of a country
#   are missing — in that case, fill backward from the first available value.
#
# We must do this WITHIN each country separately, not across all rows.
# groupby('country') splits the data per country before filling.
# group_keys=False avoids adding an extra index level.

df = df.sort_values(['country', 'year']).reset_index(drop=True)

# Group columns by filling behavior
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

# Apply group-wise ffill and fillna(0) for zero-fill columns (renewables and energy consumption)
for col in zero_fill_cols:
    df[col] = df.groupby('country')[col].transform(lambda x: x.ffill().fillna(0))

# Apply group-wise ffill only for nan-fill columns (demographics, economics, intensity)
for col in nan_fill_cols:
    df[col] = df.groupby('country')[col].transform(lambda x: x.ffill())

print("--- STEP 5: Missing Values Handled ---")
missing_after = df.isnull().sum()
print("Remaining NaN per column (only showing columns with NaN):")
print(missing_after[missing_after > 0])
print()


# =============================================================================
# STEP 6: COMPUTE DERIVED METRICS
# =============================================================================

# --- 6a: CO₂ per Capita ---
# greenhouse_gas_emissions is in million tonnes (Mt)
# population is in absolute count
# To get tonnes per person: (Mt * 1,000,000) / population
# The result is in tonnes of CO₂ per person per year

df['co2_per_capita'] = (df['greenhouse_gas_emissions'] * 1e6) / df['population']

# --- 6b: GDP per Capita ---
# gdp is total GDP in international dollars
# gdp_per_capita gives us the economic output per person

df['gdp_per_capita'] = df['gdp'] / df['population']

# --- 6c & 6d: GDP Index and CO₂ Index (Normalized to 100 at Year 2000) ---
# For the Decoupling Gap chart (Task 4.3), we need to compare GDP growth
# and CO₂ growth on the SAME scale, regardless of a country's original values.
#
# Method: for each country, divide every year's value by the 2000 value × 100.
# So year 2000 = 100 for every country. If a country's GDP grows 50% by 2010,
# its gdp_index in 2010 = 150. If CO₂ drops 10%, co2_index = 90.
#
# Decoupling Gap = gdp_index - co2_index
# If this is positive and growing → the economy is growing while emissions fall.

# Get the year-2000 baseline values for each country
base_2000 = df[df['year'] == 2000][['country', 'gdp_per_capita', 'co2_per_capita']].copy()
base_2000 = base_2000.rename(columns={
    'gdp_per_capita': 'gdp_base_2000',
    'co2_per_capita': 'co2_base_2000'
})

# Merge the 2000 baseline back into the main dataframe
# Each row now knows its country's year-2000 values
df = df.merge(base_2000, on='country', how='left')

# Compute the indices
df['gdp_index'] = (df['gdp_per_capita'] / df['gdp_base_2000']) * 100
df['co2_index'] = (df['co2_per_capita'] / df['co2_base_2000']) * 100

# Compute the decoupling gap
df['decoupling_gap'] = df['gdp_index'] - df['co2_index']

# --- 6e: Change in Renewable Share Since 2000 ---
# For Choropleth (Task 4.1) and Bubble Chart (Task 4.4).
# Shows how much each country's renewable share has CHANGED since 2000.
# A country that went from 10% → 30% has a change of +20 percentage points.

base_renew = df[df['year'] == 2000][['country', 'renewables_share_energy']].copy()
base_renew = base_renew.rename(columns={'renewables_share_energy': 'renew_share_2000'})

df = df.merge(base_renew, on='country', how='left')

df['renewable_share_change'] = df['renewables_share_energy'] - df['renew_share_2000']

# --- 6f: Tapio Decoupling Elasticity & Status ---
import numpy as np

# Compute percentage changes relative to 2000
df['pct_change_gdp'] = (df['gdp_per_capita'] - df['gdp_base_2000']) / df['gdp_base_2000']
df['pct_change_co2'] = (df['co2_per_capita'] - df['co2_base_2000']) / df['co2_base_2000']

# Compute Tapio elasticity (handling division by zero)
df['tapio_elasticity'] = np.where(
    df['pct_change_gdp'].abs() > 1e-5,
    df['pct_change_co2'] / df['pct_change_gdp'],
    np.nan
)

# Classify decoupling status for each country-year (handling NaN input data)
df['decoupling_status'] = None
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] < 0), 'decoupling_status'] = 'Strong Decoupling'
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] >= 0) & (df['tapio_elasticity'] < 0.8), 'decoupling_status'] = 'Weak Decoupling'
df.loc[(df['pct_change_gdp'] > 0) & (df['pct_change_co2'] >= 0) & (df['tapio_elasticity'] >= 0.8), 'decoupling_status'] = 'Coupled'
df.loc[(df['pct_change_gdp'] <= 0), 'decoupling_status'] = 'Coupled'

# Find 2022 decoupling status for each country and merge it back for Task 4.4 Bubble Chart
status_2022 = df[df['year'] == 2022][['country', 'decoupling_status']].copy()
status_2022 = status_2022.rename(columns={'decoupling_status': 'decoupling_status_2022'})

df = df.merge(status_2022, on='country', how='left')

print("--- STEP 6: Derived Metrics Computed ---")
print("New columns added:")
new_cols = ['co2_per_capita', 'gdp_per_capita', 'gdp_index', 'co2_index',
            'decoupling_gap', 'renewable_share_change', 'tapio_elasticity', 'decoupling_status', 'decoupling_status_2022']
print(new_cols)
print()


# =============================================================================
# STEP 7: SAVE OUTPUT FILES
# =============================================================================
# We create 3 output files in a 'cleaned/' subfolder:
#
#   cleaned_all_countries.csv  → All real countries, 2000–2022 (used for
#                                 bubble chart background ~150 grey bubbles)
#
#   cleaned_8_countries.csv    → Only the 8 default countries (used for most
#                                 of the 6 visualization tasks)
#
#   summary_2022.csv           → Single-year snapshot for 2022 (all countries)
#                                 Good for choropleth and bubble chart starting state

os.makedirs('cleaned', exist_ok=True)

# --- All countries ---
df.to_csv('cleaned/cleaned_all_countries.csv', index=False)
print("Saved: cleaned/cleaned_all_countries.csv")

# --- 8 Default Countries ---
# Note: "USA" in OWID dataset is stored as "United States"
eight_countries = [
    'Denmark', 'France', 'India', 'Morocco',
    'Brazil', 'United States', 'China', 'Indonesia'
]
df_8 = df[df['country'].isin(eight_countries)]
df_8.to_csv('cleaned/cleaned_8_countries.csv', index=False)
print("Saved: cleaned/cleaned_8_countries.csv")
print(f"  Countries found: {df_8['country'].unique().tolist()}")

# --- 2022 Snapshot (all countries) ---
df_2022 = df[df['year'] == 2022].copy()
df_2022.to_csv('cleaned/summary_2022.csv', index=False)
print("Saved: cleaned/summary_2022.csv")

print()
print("=== ALL DONE ===")
print(f"cleaned_all_countries : {df.shape}")
print(f"cleaned_8_countries   : {df_8.shape}")
print(f"summary_2022          : {df_2022.shape}")


# =============================================================================
# STEP 8: QUICK SANITY CHECKS
# =============================================================================
# Run these to verify the data looks correct before building visualizations.

print("\n--- SANITY CHECK: India renewable share trend ---")
india = df_8[df_8['country'] == 'India'][['year', 'renewables_share_energy', 'decoupling_gap']]
print(india.to_string(index=False))

print("\n--- SANITY CHECK: Decoupling status in 2022 ---")
check = df_8[df_8['year'] == 2022][['country', 'gdp_index', 'co2_index', 'decoupling_gap', 'decoupling_status_2022']]
print(check.to_string(index=False))
