import dash
from dash import dcc, html, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd
from data_loader import df_2022, all_countries
from config import CUSTOM_COLORS, COLOR_PALETTE

# Task 4.6 Layout
layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Select Peers to Compare:', className='controls-label', style={'marginRight': '12px', 'fontWeight': 'bold'}),
            html.Div(
                dcc.Dropdown(
                    id='radar-country-dropdown',
                    options=[{'label': c, 'value': c} for c in all_countries],
                    value=['India', 'China', 'Brazil', 'Morocco', 'Indonesia'],
                    multi=True,
                    placeholder='Select peers...',
                    style={'fontSize': '12px', 'minWidth': '320px'}
                ),
                style={'flex': 1, 'maxWidth': '450px'}
            ),
            html.Div('(Global Average is always included)', className='controls-label', style={'fontSize': '10px', 'opacity': 0.75}),
        ], className='chart-controls'),
        html.Div([
            dcc.Graph(id='radar-chart', style={'height': '100%', 'width': '100%'}, responsive=True),
            html.Button('↺ Reset Peers', id='radar-reset-btn', className='chart-reset-btn', style={'position': 'absolute', 'bottom': '15px', 'right': '15px', 'zIndex': 10}),
        ], className='chart-body', style={'position': 'relative'}),
    ], className='chart-card'),
], id='page-radar', className='page-panel')

# Task 4.6 Callbacks
@callback(
    Output('radar-chart', 'figure'),
    Input('radar-country-dropdown', 'value')
)
def update_radar(selected_peers):
    selected_peers = selected_peers or []

    CORE_METRICS = ['renewables_share_energy', 'renewable_share_change', 'co2_per_capita',
                    'per_capita_electricity', 'energy_efficiency', 'fossil_share_energy']
    AXIS_LABELS = ['Renewable %', 'Renew Growth', 'CO₂ (Inv)', 'Elec kWh', 'Efficiency', 'Fossil (Inv)']

    g_avg_vals = df_2022[CORE_METRICS].mean()
    g_avg_row = pd.DataFrame([{
        'country': 'Global Average',
        **{m: g_avg_vals[m] for m in CORE_METRICS}
    }])
    df_comb = pd.concat([df_2022, g_avg_row], ignore_index=True).fillna(0)

    # Plot list contains the selected peers plus India (if not present) and Global Average
    plot_list = list(selected_peers)
    if 'India' not in plot_list:
        plot_list.append('India')
    if 'Global Average' not in plot_list:
        plot_list.append('Global Average')

    # Filter df_comb to only contain the selected peer countries + Global Average
    # reset_index ensures 0-based contiguous indexing so pandas assignment is safe
    df_peers = df_comb[df_comb['country'].isin(plot_list)].reset_index(drop=True).copy()

    # Normalize ONLY based on min/max of df_peers (pure peer-group normalization)
    df_norm = df_peers.copy()
    for col in CORE_METRICS:
        mn, mx = df_peers[col].min(), df_peers[col].max()
        if mx == mn:
            df_norm.loc[:, col] = 50.0
            continue
        ns = ((df_peers[col] - mn) / (mx - mn)) * 100
        df_norm.loc[:, col] = (100 - ns) if col in ['co2_per_capita', 'fossil_share_energy'] else ns

    # Build per-country color map: known → CUSTOM_COLORS, Global Avg → grey,
    # extra countries → cycle through palette colors not already used
    used_colors = set(CUSTOM_COLORS.values())
    extra_palette = [c for c in COLOR_PALETTE if c not in used_colors]
    extra_idx = 0
    country_colors = {}
    for c in plot_list:
        if c in CUSTOM_COLORS:
            country_colors[c] = CUSTOM_COLORS[c]
        elif c == 'Global Average':
            country_colors[c] = '#9B8470'
        else:
            country_colors[c] = extra_palette[extra_idx % len(extra_palette)]
            extra_idx += 1

    fig = go.Figure()
    for country in plot_list:
        c_norm = df_norm[df_norm['country'] == country]
        if c_norm.empty:
            continue
        c_raw = df_peers[df_peers['country'] == country].iloc[0]
        rv = [c_norm[m].values[0] for m in CORE_METRICS]
        rv.append(rv[0])
        th = list(AXIS_LABELS) + [AXIS_LABELS[0]]
        col = country_colors[country]
        ht = (f'<b>{country}</b><br>'
              f'Renewable Share: {c_raw["renewables_share_energy"]:.1f}%<br>'
              f'Renewable Growth: {c_raw["renewable_share_change"]:+.1f} pp<br>'
              f'CO₂ per Capita: {c_raw["co2_per_capita"]:.2f} t<br>'
              f'Electricity per Capita: {c_raw["per_capita_electricity"]:,.0f} kWh<br>'
              f'Energy Efficiency: ${c_raw["energy_efficiency"]:.2f} GDP/kWh<br>'
              f'Fossil Share: {c_raw["fossil_share_energy"]:.1f}%<extra></extra>')
        fig.add_trace(go.Scatterpolar(
            r=rv, theta=th, fill='toself', name=country,
            line=dict(color=col, width=2.5),
            fillcolor=col,
            opacity=0.25,
            hovertemplate=ht
        ))
        # Solid border trace
        fig.add_trace(go.Scatterpolar(
            r=rv, theta=th, name=country, showlegend=False,
            line=dict(color=col, width=2.5),
            mode='lines',
            hovertemplate=ht
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor='#E8DDD0', tickfont=dict(size=9), showticklabels=True),
            angularaxis=dict(gridcolor='#E8DDD0', linecolor='#C4B090',
                             tickfont=dict(size=12, family='Inter', color='#4A3520'))
        ),
        showlegend=True,
        legend=dict(x=1.05, y=1, xanchor='left', yanchor='top', font=dict(size=12),
                    bgcolor='rgba(255,250,240,0.9)', bordercolor='#D4B870', borderwidth=1),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=160, t=30, b=50),
        font=dict(family='Inter')
    )
    return fig

@callback(
    Output('radar-country-dropdown', 'value'),
    Input('radar-reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_radar_peers(n_clicks):
    return ['India', 'China', 'Brazil', 'Morocco', 'Indonesia']
