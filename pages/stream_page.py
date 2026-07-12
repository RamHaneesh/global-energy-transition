from dash import dcc, html, callback, Output, Input
import plotly.graph_objects as go
from data_loader import df_global
from config import ENERGY_SOURCES, SOURCE_LABELS, SOURCE_COLORS

# Task 4.2 Layout
layout = html.Div([
    html.Div([
        html.Div([
            html.Div('View Mode', className='controls-label'),
            dcc.RadioItems(
                id='stream-view-mode',
                options=[
                    {'label': 'Share (%)',       'value': 'percent'},
                    {'label': 'Absolute (TWh)', 'value': 'absolute'}
                ],
                value='percent',
                inline=True,
                inputStyle={'marginRight': '4px', 'marginLeft': '12px'},
                labelStyle={'fontSize': '12px', 'color': '#5C3D18'},
                className='dcc-radio'
            ),
        ], className='chart-controls'),

        # Legend
        html.Div([
            html.Div([
                html.Div(className='legend-dot', style={'background': SOURCE_COLORS[s]}),
                html.Span(SOURCE_LABELS[s])
            ], className='legend-badge')
            for s in ENERGY_SOURCES
        ], id='stream-legend'),

        html.Div(
            dcc.Graph(id='streamgraph', style={'height': '100%', 'width': '100%'}, responsive=True),
            className='chart-body'
        ),
    ], className='chart-card'),
], id='page-stream', className='page-panel')

# Task 4.2 Callbacks
@callback(
    Output('streamgraph', 'figure'),
    Input('stream-view-mode', 'value')
)
def update_streamgraph(view_mode):
    years = df_global['year']
    if view_mode == 'percent':
        row_totals = df_global[ENERGY_SOURCES].sum(axis=1)
        plot_data = df_global[ENERGY_SOURCES].div(row_totals, axis=0) * 100
        y_label, hover_suffix = 'Share (%)', '%'
    else:
        plot_data = df_global[ENERGY_SOURCES]
        y_label, hover_suffix = 'TWh', ' TWh'

    fig = go.Figure()
    for i, source in enumerate(ENERGY_SOURCES):
        y_values = plot_data[source]
        hover_texts = [
            f'<b>{SOURCE_LABELS[source]}</b><br>Year: {year}<br>Value: {val:,.1f}{hover_suffix}'
            for year, val in zip(years, y_values)
        ]
        fig.add_trace(go.Scatter(
            x=years, y=y_values, name=SOURCE_LABELS[source], mode='lines',
            line=dict(width=0.5, color=SOURCE_COLORS[source]),
            fillcolor=SOURCE_COLORS[source],
            fill='tozeroy' if i == 0 else 'tonexty',
            stackgroup='one', opacity=0.85,
            text=hover_texts, hoverinfo='text'
        ))

    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=4, showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(title=y_label, showgrid=True, gridcolor='#F0E8D8', tickfont=dict(size=11)),
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=50, r=20, t=15, b=30),
        font=dict(family='Inter')
    )
    return fig
