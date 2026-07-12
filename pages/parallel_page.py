import dash
from dash import dcc, html, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd
from data_loader import df_2022, _valid_countries
from config import CUSTOM_COLORS, COLOR_PALETTE

# Task 4.5 Layout
layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Mode:', className='controls-label', style={'marginRight': '8px', 'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='parallel-mode-toggle',
                options=[
                    {'label': 'Selected Countries', 'value': 'selected'},
                    {'label': 'Strong Decoupled', 'value': 'Strong Decoupling'},
                    {'label': 'Weak Decoupled', 'value': 'Weak Decoupling'},
                    {'label': 'Coupled', 'value': 'Coupled'},
                    {'label': 'Decoupling Medians', 'value': 'averages'}
                ],
                value='selected',
                inline=True,
                inputStyle={'marginRight': '4px', 'marginLeft': '12px'},
                labelStyle={'fontSize': '12px', 'color': '#5C3D18', 'marginRight': '4px'},
                className='dcc-radio',
                style={'display': 'inline-block'}
            ),
            html.Div('Click & drag axis titles to reorder · Brush vertically to filter · Double-click to reset',
                     className='controls-label', style={'marginLeft': 'auto', 'opacity': 0.75, 'fontSize': '10px'}),
        ], className='chart-controls'),
        html.Div(id='parallel-legend-container', style={
            'display': 'flex', 'justifyContent': 'center', 'gap': '12px', 'flexWrap': 'wrap',
            'padding': '6px 16px', 'backgroundColor': 'rgba(255,250,240,0.4)',
            'borderBottom': '1px solid #F0E8D8', 'fontSize': '11px', 'fontFamily': 'Inter, sans-serif'
        }),
        html.Div(
            dcc.Graph(
                id='parallel-plot',
                style={'height': '100%', 'width': '100%'},
                responsive=True,
                config={
                    'modeBarButtonsToAdd': ['resetScale2d'],
                    'displayModeBar': True
                }
            ),
            className='chart-body'
        ),
    ], className='chart-card'),
], id='page-parallel', className='page-panel')

# Task 4.5 Callbacks
@callback(
    Output('parallel-plot', 'figure'),
    Output('parallel-legend-container', 'children'),
    Input('global-country-dropdown', 'value'),
    Input('parallel-mode-toggle', 'value'),
    Input('parallel-reset-counter', 'data')
)
def update_parallel_plot(selected_countries, display_mode, reset_counter):
    selected_countries = selected_countries or []

    # 1. Filter valid countries for 2022 (max renewables > 0)
    valid_df_2022 = df_2022[df_2022['country'].isin(_valid_countries)].copy()

    cols_to_plot = ['gdp_per_capita', 'renewable_share_change', 'co2_per_capita',
                    'per_capita_electricity', 'fossil_share_energy']

    valid_df_2022 = valid_df_2022.dropna(subset=cols_to_plot, how='all')
    valid_df_2022[cols_to_plot] = valid_df_2022[cols_to_plot].fillna(0)

    # Calculate Global Baseline (Median for averages mode, Mean for other modes)
    if display_mode == 'averages':
        ref_avg = {
            'country': 'Global Median',
            'gdp_per_capita':          valid_df_2022['gdp_per_capita'].median(),
            'renewable_share_change':  valid_df_2022['renewable_share_change'].median(),
            'co2_per_capita':          valid_df_2022['co2_per_capita'].median(),
            'per_capita_electricity':  valid_df_2022['per_capita_electricity'].median(),
            'fossil_share_energy':     valid_df_2022['fossil_share_energy'].median()
        }
    else:
        ref_avg = {
            'country': 'Global Average',
            'gdp_per_capita':          valid_df_2022['gdp_per_capita'].mean(),
            'renewable_share_change':  valid_df_2022['renewable_share_change'].mean(),
            'co2_per_capita':          valid_df_2022['co2_per_capita'].mean(),
            'per_capita_electricity':  valid_df_2022['per_capita_electricity'].mean(),
            'fossil_share_energy':     valid_df_2022['fossil_share_energy'].mean()
        }

    # Determine list of countries to display or build averages dataframe
    if display_mode == 'averages':
        # Calculate medians for each group
        strong_df = valid_df_2022[valid_df_2022['decoupling_status'] == 'Strong Decoupling']
        weak_df = valid_df_2022[valid_df_2022['decoupling_status'] == 'Weak Decoupling']
        coupled_df = valid_df_2022[valid_df_2022['decoupling_status'] == 'Coupled']

        strong_median = {
            'country': 'Strong Decoupled Median',
            'gdp_per_capita':          strong_df['gdp_per_capita'].median() if not strong_df.empty else 0,
            'renewable_share_change':  strong_df['renewable_share_change'].median() if not strong_df.empty else 0,
            'co2_per_capita':          strong_df['co2_per_capita'].median() if not strong_df.empty else 0,
            'per_capita_electricity':  strong_df['per_capita_electricity'].median() if not strong_df.empty else 0,
            'fossil_share_energy':     strong_df['fossil_share_energy'].median() if not strong_df.empty else 0
        }

        weak_median = {
            'country': 'Weak Decoupled Median',
            'gdp_per_capita':          weak_df['gdp_per_capita'].median() if not weak_df.empty else 0,
            'renewable_share_change':  weak_df['renewable_share_change'].median() if not weak_df.empty else 0,
            'co2_per_capita':          weak_df['co2_per_capita'].median() if not weak_df.empty else 0,
            'per_capita_electricity':  weak_df['per_capita_electricity'].median() if not weak_df.empty else 0,
            'fossil_share_energy':     weak_df['fossil_share_energy'].median() if not weak_df.empty else 0
        }

        coupled_median = {
            'country': 'Coupled Median',
            'gdp_per_capita':          coupled_df['gdp_per_capita'].median() if not coupled_df.empty else 0,
            'renewable_share_change':  coupled_df['renewable_share_change'].median() if not coupled_df.empty else 0,
            'co2_per_capita':          coupled_df['co2_per_capita'].median() if not coupled_df.empty else 0,
            'per_capita_electricity':  coupled_df['per_capita_electricity'].median() if not coupled_df.empty else 0,
            'fossil_share_energy':     coupled_df['fossil_share_energy'].median() if not coupled_df.empty else 0
        }

        df_plot = pd.DataFrame([strong_median, weak_median, coupled_median])
    else:
        if display_mode == 'selected':
            target_list = selected_countries
        else:
            # One of the decoupling statuses: 'Strong Decoupling', 'Weak Decoupling', 'Coupled'
            target_list = valid_df_2022[valid_df_2022['decoupling_status'] == display_mode]['country'].tolist()

        # 2. Build foreground dataset
        fg_df = valid_df_2022[valid_df_2022['country'].isin(target_list)].copy()

        # Sort if in selected mode to match selection list order, otherwise sort alphabetically
        if display_mode == 'selected':
            sort_order = {country: idx for idx, country in enumerate(selected_countries)}
            fg_df['sort_idx'] = fg_df['country'].map(sort_order)
            fg_df = fg_df.sort_values('sort_idx').drop(columns=['sort_idx'])
        else:
            fg_df = fg_df.sort_values('country')

        if display_mode == 'selected':
            avg_df = pd.DataFrame([ref_avg])
            df_plot = pd.concat([avg_df, fg_df], ignore_index=True)
        else:
            df_plot = fg_df

    # 3. Assign color IDs and resolve color scale
    # If selected mode: 0 = Global Average, 1, 2, 3... = individual colors
    # If averages mode: 0 = Strong Median, 1 = Weak Median, 2 = Coupled Median (no Global Median)
    # If status modes: 0 = Global Average, 1 = status color
    color_ids = []
    for _, row in df_plot.iterrows():
        c_name = row['country']
        if display_mode == 'averages':
            if c_name == 'Strong Decoupled Median':
                color_ids.append(0)
            elif c_name == 'Weak Decoupled Median':
                color_ids.append(1)
            else:
                color_ids.append(2)
        else:
            if c_name in ['Global Average', 'Global Median']:
                color_ids.append(0)
            else:
                if display_mode == 'selected':
                    idx = selected_countries.index(c_name)
                    color_ids.append(1 + idx)
                else:
                    color_ids.append(1)
    df_plot['line_color_id'] = color_ids

    # Helper for resolving color
    def get_color(color_id):
        if display_mode == 'averages':
            if color_id == 0:
                return '#2ca02c'  # Strong Median (Green)
            elif color_id == 1:
                return '#ff7f0e'  # Weak Median (Orange/Yellow)
            else:
                return '#d62728'  # Coupled Median (Red)
        else:
            if color_id == 0:
                return '#A09080'  # Global Average / Median (brown/gold)
            else:
                if display_mode == 'selected':
                    idx = color_id - 1
                    country_name = selected_countries[idx]
                    return CUSTOM_COLORS.get(country_name, COLOR_PALETTE[idx % len(COLOR_PALETTE)])
                else:
                    # Semantic group colors:
                    if display_mode == 'Strong Decoupling':
                        return '#2ca02c'  # Green
                    elif display_mode == 'Weak Decoupling':
                        return '#ff7f0e'  # Orange/Yellow
                    else:
                        return '#d62728'  # Red

    # Step-wise Colorscale
    if display_mode == 'selected':
        n_colors = 1 + len(selected_countries)
    elif display_mode == 'averages':
        n_colors = 3
    else:
        n_colors = 1

    if n_colors == 1:
        group_color = get_color(1)
        colorscale = [[0, group_color], [1, group_color]]
    else:
        colorscale = []
        for i in range(n_colors):
            color = get_color(i)
            if i == 0:
                colorscale.append([0.0, color])
                colorscale.append([0.5 / (n_colors - 1), color])
            elif i == n_colors - 1:
                colorscale.append([(n_colors - 1.5) / (n_colors - 1), color])
                colorscale.append([1.0, color])
            else:
                colorscale.append([(i - 0.5) / (n_colors - 1), color])
                colorscale.append([(i + 0.5) / (n_colors - 1), color])

    # 4. Dimensions list mapped to raw physical values (with outlier clamping to prevent bleeding)
    # Order: Fossil% ──> CO2 per Capita ──> Electricity per Capita ──> Renewable% ──> Renewable Growth
    dimensions = [
        dict(range=[0, 100], label='Fossil Share (%)', values=df_plot['fossil_share_energy'],
             tickvals=[0, 20, 40, 60, 80, 100], ticktext=['0%', '20%', '40%', '60%', '80%', '100%']),
        dict(range=[0, 25],  label='CO₂ per Capita (t)', values=df_plot['co2_per_capita'].clip(upper=25),
             tickvals=[0, 5, 10, 15, 20, 25], ticktext=['0', '5t', '10t', '15t', '20t', '25t']),
        dict(range=[0, 30000], label='Electricity per Capita (kWh)', values=df_plot['per_capita_electricity'].clip(upper=30000),
             tickvals=[0, 5000, 10000, 15000, 20000, 25000, 30000], ticktext=['0', '5k', '10k', '15k', '20k', '25k', '30k']),
        dict(range=[0, 100000], label='GDP per Capita ($)', values=df_plot['gdp_per_capita'].clip(upper=100000),
             tickvals=[0, 20000, 40000, 60000, 80000, 100000], ticktext=['0', '$20k', '$40k', '$60k', '$80k', '$100k']),
        dict(range=[-10, 40], label='Renew. Growth (pp since 2000)', values=df_plot['renewable_share_change'].clip(lower=-10, upper=40),
             tickvals=[-10, 0, 10, 20, 30, 40], ticktext=['-10pp', '0', '10pp', '20pp', '30pp', '40pp']),
    ]

    parcoords = go.Parcoords(
        line=dict(color=df_plot['line_color_id'], colorscale=colorscale, showscale=False),
        dimensions=dimensions, labelangle=0, labelside='bottom',
        labelfont=dict(size=11, family='Inter', color='#4A3520')
    )
    fig = go.Figure(data=parcoords)

    # 5. Build HTML Legend
    legend_children = []
    if display_mode == 'selected':
        for idx, name in enumerate(selected_countries):
            col = get_color(1 + idx)
            legend_children.append(html.Div([
                html.Div(style={
                    'background': col, 'width': '8px', 'height': '8px',
                    'borderRadius': '50%', 'marginRight': '6px', 'flexShrink': 0
                }),
                html.Span(name, style={'color': '#5C3D18', 'fontWeight': '600'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '16px', 'padding': '2px 0'}))
    elif display_mode == 'averages':
        # 3 Medians Legend (no Global Median)
        legend_children = [
            html.Div([
                html.Div(style={
                    'background': '#2ca02c', 'width': '8px', 'height': '8px',
                    'borderRadius': '50%', 'marginRight': '6px', 'flexShrink': 0
                }),
                html.Span('Strong Decoupled Median', style={'color': '#5C3D18', 'fontWeight': '600'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '16px', 'padding': '2px 0'}),
            html.Div([
                html.Div(style={
                    'background': '#ff7f0e', 'width': '8px', 'height': '8px',
                    'borderRadius': '50%', 'marginRight': '6px', 'flexShrink': 0
                }),
                html.Span('Weak Decoupled Median', style={'color': '#5C3D18', 'fontWeight': '600'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '16px', 'padding': '2px 0'}),
            html.Div([
                html.Div(style={
                    'background': '#d62728', 'width': '8px', 'height': '8px',
                    'borderRadius': '50%', 'marginRight': '6px', 'flexShrink': 0
                }),
                html.Span('Coupled Median', style={'color': '#5C3D18', 'fontWeight': '600'})
            ], style={'display': 'flex', 'alignItems': 'center', 'padding': '2px 0'})
        ]
    else:
        col = get_color(1)
        name_map = {
            'Strong Decoupling': 'Strong Decoupled Countries',
            'Weak Decoupling': 'Weak Decoupled Countries',
            'Coupled': 'Coupled / Fossil-Locked Countries'
        }
        legend_children.append(html.Div([
            html.Div(style={
                'background': col, 'width': '8px', 'height': '8px',
                'borderRadius': '50%', 'marginRight': '6px', 'flexShrink': 0
            }),
            html.Span(name_map[display_mode], style={'color': '#5C3D18', 'fontWeight': '600'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '16px', 'padding': '2px 0'}))

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter'),
        showlegend=False,
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        margin=dict(l=75, r=75, t=25, b=45),
        uirevision=reset_counter
    )
    return fig, legend_children

@callback(
    Output('parallel-reset-counter', 'data'),
    Input('parallel-plot', 'relayoutData'),
    State('parallel-reset-counter', 'data'),
    prevent_initial_call=True
)
def detect_parallel_reset(relayout_data, current):
    if relayout_data:
        if 'autosize' in relayout_data or 'xaxis.autorange' in relayout_data:
            return (current or 0) + 1
    return dash.no_update
