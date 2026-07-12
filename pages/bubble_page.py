import dash
from dash import dcc, html, callback, Output, Input, State, ctx
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from data_loader import df_all, df_bubble_clean
from config import CUSTOM_COLORS, COLOR_PALETTE

# Task 4.4 Layout
layout = html.Div([
    html.Div([
        html.Div([
            html.Div('X: Δ Renewable Share  ·  Y: Δ CO₂ per Capita  ·  Color: Decoupling status  ·  Bubble size = GDP per capita', className='controls-label'),
        ], className='chart-controls'),
        html.Div(
            dcc.Graph(id='bubble-chart', style={'height': '100%', 'width': '100%'}, responsive=True),
            className='chart-body'
        ),
    ], className='chart-card'),
], id='page-bubble', className='page-panel')

# Task 4.4 Callbacks
@callback(
    Output('bubble-chart', 'figure'),
    Input('global-country-dropdown', 'value'),
    Input('bubble-reset-counter', 'data'),
    Input('bubble-clicked-country', 'data')
)
def update_bubble_chart(highlighted_countries, reset_counter, clicked_country):
    highlighted_countries = highlighted_countries or []

    bg_data = df_bubble_clean[~df_bubble_clean['country'].isin(highlighted_countries)].copy()
    fg_data = df_bubble_clean[df_bubble_clean['country'].isin(highlighted_countries)].copy()

    max_gdp = df_bubble_clean['gdp_per_capita'].max()

    def get_sizes(gdp_series, is_fg=False):
        base_size = 28 if is_fg else 9
        return np.clip(base_size * np.sqrt(gdp_series / max_gdp), 3 if not is_fg else 10, 42)

    fig = go.Figure()

    # ── Shaded quadrant backgrounds ──
    x_mid, y_mid = 0, 0
    x_min, x_max = -11, 43
    y_min, y_max = -4.8, 4.8
    fig.add_shape(type='rect', x0=x_mid, y0=y_min, x1=x_max, y1=y_mid,
                  fillcolor='rgba(44,160,44,0.06)', line_width=0, layer='below')
    fig.add_shape(type='rect', x0=x_mid, y0=y_mid, x1=x_max, y1=y_max,
                  fillcolor='rgba(214,39,40,0.06)', line_width=0, layer='below')
    fig.add_shape(type='rect', x0=x_min, y0=y_min, x1=x_mid, y1=y_mid,
                  fillcolor='rgba(180,180,180,0.06)', line_width=0, layer='below')
    fig.add_shape(type='rect', x0=x_min, y0=y_mid, x1=x_mid, y1=y_max,
                  fillcolor='rgba(214,39,40,0.06)', line_width=0, layer='below')

    # ── Background bubbles coloured by data-driven decoupling status ──
    for status_val, bg_color, bg_border, bg_name in [
        ('Strong Decoupling', '#a3e2a3', '#4a9e4a', 'Others (Strong Decoupling)'),
        ('Weak Decoupling',   '#ffe099', '#e69500', 'Others (Weak Decoupling)'),
        ('Coupled',           '#f8b1b1', '#c04040', 'Others (Coupled)')
    ]:
        sub = bg_data[bg_data['decoupling_status_2022'] == status_val]
        if sub.empty:
            continue
        hover = [
            f'<b>{r["country"]}</b><br>Δ Renewables: {r["renewable_share_change"]:+.1f}%'
            f'<br>Δ CO₂: {r["co2_change"]:+.2f}t<br>GDP: ${r["gdp_per_capita"]:,.0f}'
            f'<br>Tapio Decoupling: {r["decoupling_status_2022"]}'
            for _, r in sub.iterrows()
        ]
        fig.add_trace(go.Scatter(
            x=sub['renewable_share_change'], y=sub['co2_change'], mode='markers',
            marker=dict(size=get_sizes(sub['gdp_per_capita']), color=bg_color,
                        opacity=0.45, line=dict(width=0.5, color=bg_border)),
            name=bg_name, text=hover, hoverinfo='text',
            customdata=sub['country'].tolist()
        ))

    # ── Foreground highlighted countries, coloured by data decoupling ──
    label_positions = ['top center', 'middle right', 'bottom center', 'middle left',
                       'top right', 'bottom right', 'top left', 'bottom left']
    for idx, (status_val, color, label) in enumerate([
        ('Strong Decoupling', '#2ca02c', 'Strong Decoupling'),
        ('Weak Decoupling',   '#ff7f0e', 'Weak Decoupling'),
        ('Coupled',           '#d62728', 'Coupled')
    ]):
        status_data = fg_data[fg_data['decoupling_status_2022'] == status_val]
        if status_data.empty:
            continue
        fg_hover = [
            f'<b>{r["country"]}</b><br>Δ Renewables: {r["renewable_share_change"]:+.1f}%'
            f'<br>Δ CO₂: {r["co2_change"]:+.2f}t<br>GDP: ${r["gdp_per_capita"]:,.0f}'
            f'<br>Tapio Decoupling: {r["decoupling_status_2022"]}'
            for _, r in status_data.iterrows()
        ]
        # Alternate label positions to reduce overlap
        text_positions = [
            label_positions[i % len(label_positions)]
            for i in range(len(status_data))
        ]
        fig.add_trace(go.Scatter(
            x=status_data['renewable_share_change'], y=status_data['co2_change'],
            mode='markers+text',
            marker=dict(size=get_sizes(status_data['gdp_per_capita'], is_fg=True),
                        color=color, opacity=0.92,
                        line=dict(width=1.5, color='white'),
                        symbol='circle'),
            text=status_data['country'].tolist(),
            hovertext=fg_hover,
            textposition=text_positions,
            textfont=dict(family='Inter', size=11, color='#1A1A1A'),
            name=label, hoverinfo='text',
            customdata=status_data['country'].tolist()
        ))

    # ── Trajectory for clicked country ──
    if clicked_country:
        traj_df = df_all[df_all['country'] == clicked_country].sort_values('year')
        traj_df = traj_df[traj_df['renewables_share_energy'].notna() &
                          traj_df['co2_per_capita'].notna() &
                          traj_df['renew_share_2000'].notna() &
                          traj_df['co2_base_2000'].notna()]
        if not traj_df.empty:
            traj_x = (traj_df['renewables_share_energy'] - traj_df['renew_share_2000']).tolist()
            traj_y = (traj_df['co2_per_capita']          - traj_df['co2_base_2000']).tolist()
            years   = traj_df['year'].tolist()
            t_color = CUSTOM_COLORS.get(clicked_country, '#555555')

            # Path line
            fig.add_trace(go.Scatter(
                x=traj_x, y=traj_y, mode='lines',
                line=dict(color=t_color, width=1.5, dash='dot'),
                showlegend=False, hoverinfo='skip', name='_traj_line'
            ))
            # Year dots with hover
            hover_traj = [f'<b>{clicked_country} ({y})</b><br>Δ Renew: {x:+.1f}%<br>Δ CO₂: {yv:+.2f}t'
                          for y, x, yv in zip(years, traj_x, traj_y)]
            fig.add_trace(go.Scatter(
                x=traj_x, y=traj_y, mode='markers',
                marker=dict(
                    size=6, color=years,
                    colorscale=[[0, '#ffffff'], [1, t_color]],
                    cmin=2000, cmax=2022,
                    line=dict(width=1, color=t_color)
                ),
                text=hover_traj, hoverinfo='text',
                showlegend=False, name='_traj_dots'
            ))
            # Annotate key years
            for key_yr in [2000, 2005, 2010, 2015, 2022]:
                row = traj_df[traj_df['year'] == key_yr]
                if row.empty:
                    continue
                kx = float(row['renewables_share_energy'].values[0] - row['renew_share_2000'].values[0])
                ky = float(row['co2_per_capita'].values[0]          - row['co2_base_2000'].values[0])
                fig.add_annotation(
                    x=kx, y=ky, text=str(key_yr), showarrow=False,
                    font=dict(size=8, color=t_color, family='Inter'),
                    yshift=10
                )

    # ── Axis dividers ──
    fig.add_shape(type='line', x0=0, y0=y_min, x1=0, y1=y_max,
                  line=dict(color='#9B8470', width=1, dash='dash'))
    fig.add_shape(type='line', x0=x_min, y0=0, x1=x_max, y1=0,
                  line=dict(color='#9B8470', width=1, dash='dash'))

    # ── Quadrant labels ──
    for text, x, y, qcolor in [
        ('More Renew.<br>Less CO₂',  33, -4.2, '#2D6A2D'),
        ('More Renew.<br>More CO₂',  33,  4.2, '#8B3A3A'),
        ('Less Renew.<br>Less CO₂',  -8, -4.2, '#5C7A5C'),
        ('Less Renew.<br>More CO₂',  -8,  4.2, '#8B3A3A'),
    ]:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           font=dict(size=9, color=qcolor, family='Inter'),
                           align='center', opacity=0.65)

    fig.update_layout(
        xaxis=dict(title='Δ Renewable Share (%) since 2000', range=[x_min, x_max],
                   showgrid=True, gridcolor='#F0E8D8', tickfont=dict(size=11)),
        yaxis=dict(title='Δ CO₂ per Capita (tonnes) since 2000', range=[y_min, y_max],
                   showgrid=True, gridcolor='#F0E8D8', tickfont=dict(size=11)),
        plot_bgcolor='white', paper_bgcolor='white',
        showlegend=True,
        legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top', font=dict(size=10),
                    bgcolor='rgba(255,255,255,0.88)', bordercolor='#D0C0A0', borderwidth=1),
        margin=dict(l=55, r=20, t=15, b=50),
        font=dict(family='Inter'),
        uirevision=reset_counter
    )
    return fig

@callback(
    Output('bubble-clicked-country', 'data'),
    Input('bubble-chart', 'clickData'),
    Input('bubble-reset-counter', 'data'),
    State('bubble-clicked-country', 'data'),
    prevent_initial_call=True
)
def handle_bubble_click(click_data, reset_counter, current_clicked):
    triggered = ctx.triggered_id
    if triggered == 'bubble-reset-counter':
        return None
    if not click_data:
        return dash.no_update
    point = click_data['points'][0]
    country = point.get('customdata')
    if not country:
        return None
    if country == current_clicked:
        return None
    return country

@callback(
    Output('bubble-reset-counter', 'data'),
    Input('bubble-chart', 'relayoutData'),
    State('bubble-reset-counter', 'data'),
    prevent_initial_call=True
)
def detect_bubble_reset(relayout_data, current):
    if relayout_data:
        if 'autosize' in relayout_data or 'xaxis.autorange' in relayout_data:
            return (current or 0) + 1
    return dash.no_update
