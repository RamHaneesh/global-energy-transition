from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from data_loader import df_all
from config import CUSTOM_COLORS, COLOR_PALETTE

# Task 4.3 Layout
layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Countries selected in sidebar · Y-axis: Tapio Elasticity (β) = %ΔCO₂ / %ΔGDP (relative to year 2000)', className='controls-label', style={'flex': '1'}),
            # Floating Guide Trigger Button
            html.Button(
                "ℹ️ Tapio Guide",
                id="tapio-guide-btn",
                n_clicks=0,
                style={
                    'cursor': 'pointer', 'fontSize': '11px', 'color': '#8B6430', 'fontWeight': '500',
                    'backgroundColor': '#FAF7F2', 'border': '1px solid #F0E8D8', 'borderRadius': '4px',
                    'padding': '3px 8px', 'marginLeft': '10px', 'outline': 'none'
                }
            ),
            # Bootstrap Popover
            dbc.Popover(
                [
                    dbc.PopoverHeader("📊 Tapio Decoupling Guide", style={'color': '#8B6430', 'fontSize': '14px', 'fontWeight': '600'}),
                    dbc.PopoverBody([
                        html.P("Decoupling measures if the economy is growing while environmental impact decreases.", style={'fontSize': '11px', 'color': '#5C3D18', 'lineHeight': '1.4', 'margin': '0 0 10px 0'}),
                        html.Div([
                            html.Div([
                                html.Span("🟢 Strong Decoupling", style={'fontWeight': 'bold', 'fontSize': '11px', 'color': '#2d6a2d'}),
                                html.P("GDP increases while absolute emissions decrease (elasticity β < 0).", style={'fontSize': '10px', 'color': '#444', 'margin': '2px 0 8px 0'})
                            ]),
                            html.Div([
                                html.Span("🟡 Weak Decoupling", style={'fontWeight': 'bold', 'fontSize': '11px', 'color': '#b27a00'}),
                                html.P("Both grow, but GDP grows much faster (elasticity 0 < β < 0.8).", style={'fontSize': '10px', 'color': '#444', 'margin': '2px 0 8px 0'})
                            ]),
                            html.Div([
                                html.Span("🔴 Coupled / Non-Decoupled", style={'fontWeight': 'bold', 'fontSize': '11px', 'color': '#a30000'}),
                                html.P("Emissions grow at similar or faster rate than GDP (elasticity β ≥ 0.8).", style={'fontSize': '10px', 'color': '#444', 'margin': '2px 0 0 0'})
                            ])
                        ], style={'padding': '10px', 'backgroundColor': '#FAF7F2', 'borderRadius': '6px', 'border': '1px solid #F0E8D8'})
                    ])
                ],
                id="tapio-guide-popover",
                target="tapio-guide-btn",
                trigger="legacy",
                placement="bottom-end",
                style={'width': '290px', 'zIndex': '1050', 'boxShadow': '0 4px 15px rgba(0,0,0,0.15)', 'border': '1px solid #F0E8D8', 'borderRadius': '8px'}
            )
        ], className='chart-controls', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}),
        html.Div([
            # Chart (takes 100% space)
            dcc.Graph(id='decoupling-chart', style={'height': '100%', 'width': '100%'}, responsive=True),
        ], className='chart-body', style={'position': 'relative', 'height': '100%'})
    ], className='chart-card'),
], id='page-decouple', className='page-panel')

# Task 4.3 Callbacks
@callback(
    Output('decoupling-chart', 'figure'),
    Input('global-country-dropdown', 'value')
)
def update_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = []

    fig = go.Figure()

    # Calculate min and max y-values from selected data to set dynamic range
    selected_data = df_all[(df_all['country'].isin(selected_countries)) & (df_all['year'] >= 2005)]
    if not selected_data.empty:
        valid_elast = selected_data['tapio_elasticity'].replace([np.inf, -np.inf], np.nan).dropna()
        if not valid_elast.empty:
            min_val = float(valid_elast.min())
            max_val = float(valid_elast.max())
            y_range = max_val - min_val
            # Add padding (at least 0.5 to avoid flat axis, or 5% of range)
            padding = max(0.5, y_range * 0.05)
            ymin = min_val - padding
            ymax = max_val + padding
        else:
            ymin, ymax = -3.0, 3.0
    else:
        ymin, ymax = -3.0, 3.0

    if ymax <= ymin:
        ymax = ymin + 1.0

    # 1. Add background bands for Tapio decoupling zones dynamically clamped to ymin/ymax
    if ymin < 0.0:
        fig.add_hrect(y0=ymin, y1=min(0.0, ymax), fillcolor="rgba(44, 160, 44, 0.06)", line_width=0,
                      annotation_text="Strong Decoupling (β < 0)" if (min(0.0, ymax) - ymin) > 0.15 else "",
                      annotation_position="bottom left",
                      annotation_font=dict(size=9, color="#2D6A2D"))
    if ymin < 0.8 and ymax > 0.0:
        fig.add_hrect(y0=max(0.0, ymin), y1=min(0.8, ymax), fillcolor="rgba(255, 159, 28, 0.06)", line_width=0,
                      annotation_text="Weak Decoupling (0 ≤ β < 0.8)" if (min(0.8, ymax) - max(0.0, ymin)) > 0.15 else "",
                      annotation_position="bottom left",
                      annotation_font=dict(size=9, color="#8B6430"))
    if ymin < 1.2 and ymax > 0.8:
        fig.add_hrect(y0=max(0.8, ymin), y1=min(1.2, ymax), fillcolor="rgba(214, 39, 40, 0.04)", line_width=0,
                      annotation_text="Coupled (0.8 ≤ β ≤ 1.2)" if (min(1.2, ymax) - max(0.8, ymin)) > 0.08 else "",
                      annotation_position="bottom left",
                      annotation_font=dict(size=9, color="#8B3A3A"))
    if ymax > 1.2:
        fig.add_hrect(y0=max(1.2, ymin), y1=ymax, fillcolor="rgba(214, 39, 40, 0.08)", line_width=0,
                      annotation_text="Negative Decoupling (β > 1.2)" if (ymax - max(1.2, ymin)) > 0.15 else "",
                      annotation_position="bottom left",
                      annotation_font=dict(size=9, color="#8B3A3A"))

    # Add threshold lines only if they lie in the visible range
    if ymin < 0 < ymax:
        fig.add_shape(type='line', x0=2005, y0=0, x1=2022, y1=0,
                      line=dict(color='#9B8470', width=1.2, dash='dash'))
    if ymin < 0.8 < ymax:
        fig.add_shape(type='line', x0=2005, y0=0.8, x1=2022, y1=0.8,
                      line=dict(color='#9B8470', width=1.2, dash='dash'))
    if ymin < 1.2 < ymax:
        fig.add_shape(type='line', x0=2005, y0=1.2, x1=2022, y1=1.2,
                      line=dict(color='#9B8470', width=1.2, dash='dash'))

    for i, country in enumerate(selected_countries):
        country_data = df_all[df_all['country'] == country].sort_values('year')
        # Skip years before 2005 to avoid early-year denominator spikes
        country_data = country_data[country_data['year'] >= 2005]
        if country_data.empty:
            continue
        color = CUSTOM_COLORS.get(country, COLOR_PALETTE[i % len(COLOR_PALETTE)])
        hover_texts = []
        for year, gap, gdp_idx, co2_idx, status, elasticity in zip(
                country_data['year'], country_data['decoupling_gap'],
                country_data['gdp_index'], country_data['co2_index'],
                country_data['decoupling_status'], country_data['tapio_elasticity']):
            gap_s = f'{gap:+.1f}' if pd.notna(gap) else 'N/A'
            gdp_s = f'{gdp_idx:.1f}' if pd.notna(gdp_idx) else 'N/A'
            co2_s = f'{co2_idx:.1f}' if pd.notna(co2_idx) else 'N/A'
            elast_s = f'{elasticity:+.2f}' if pd.notna(elasticity) else 'N/A'
            hover_texts.append(
                f'<b>{country} ({year})</b><br>'
                f'Tapio Elasticity (β): {elast_s}<br>'
                f'Decoupling Status: {status}<br>'
                f'Decoupling Gap: {gap_s}<br>'
                f'GDP Index: {gdp_s} (vs 2000)<br>'
                f'CO₂ Index: {co2_s} (vs 2000)'
            )
        fig.add_trace(go.Scatter(
            x=country_data['year'], y=country_data['tapio_elasticity'],
            name=country, mode='lines+markers',
            line=dict(color=color, width=2.5),
            marker=dict(size=5),
            text=hover_texts, hoverinfo='text'
        ))

    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=2, showgrid=True, gridcolor='#F0E8D8', tickfont=dict(size=11)),
        yaxis=dict(title='Tapio Decoupling Elasticity (β)', range=[ymin, ymax], showgrid=True, gridcolor='#F0E8D8', tickfont=dict(size=11)),
        hovermode='closest',
        plot_bgcolor='white', paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5,
                    font=dict(size=11), bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=50, r=20, t=15, b=60),
        font=dict(family='Inter')
    )
    return fig
