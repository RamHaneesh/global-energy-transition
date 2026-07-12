from dash import dcc, html, callback, Output, Input, State
import plotly.express as px
from data_loader import df_all
from config import MAP_METRICS

# Task 4.1 Layout
layout = html.Div([
    html.Div([
        # Map card
        html.Div([
            html.Div([
                html.Div('Metric', className='controls-label'),
                dcc.RadioItems(
                    id='map-metric-toggle',
                    options=[{'label': v['label'], 'value': k} for k, v in MAP_METRICS.items()],
                    value='renewables_share_energy',
                    inline=True,
                    inputStyle={'marginRight': '4px', 'marginLeft': '12px'},
                    labelStyle={'fontSize': '12px', 'color': '#5C3D18', 'marginRight': '4px'},
                    className='dcc-radio'
                ),
            ], className='chart-controls'),

            html.Div([
                html.Button('▶ Play', id='map-play-btn', n_clicks=0),
                html.Div('Year', className='controls-label', style={'marginLeft': '6px'}),
                html.Div(
                    dcc.Slider(
                        id='map-year-slider',
                        min=2000, max=2022, step=1, value=2022,
                        marks={y: str(y) for y in [2000, 2005, 2010, 2015, 2020, 2022]},
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    ),
                    style={'flex': 1}
                ),
            ], id='map-slider-row'),

            html.Div(
                dcc.Graph(id='choropleth-map', style={'height': '100%', 'width': '100%'}, responsive=True),
                className='chart-body'
            ),
        ], className='chart-card', id='map-card-inner'),
    ], style={'flex': 1, 'display': 'flex', 'flexDirection': 'column', 'minHeight': 0}),
], id='page-map', className='page-panel')

# Task 4.1 Callbacks
@callback(
    Output('choropleth-map', 'figure'),
    Input('map-year-slider', 'value'),
    Input('map-metric-toggle', 'value')
)
def update_map(selected_year, selected_metric):
    dff = df_all[df_all['year'] == selected_year].dropna(subset=[selected_metric])
    metric_info = MAP_METRICS[selected_metric]

    fig = px.choropleth(
        dff, locations='iso_code', color=selected_metric, hover_name='country',
        hover_data={'renewables_share_energy': ':.1f', 'co2_per_capita': ':.2f',
                    'renewable_share_change': ':.1f', 'iso_code': False},
        color_continuous_scale=metric_info['color_scale'],
        range_color=metric_info['range'],
        labels={
            'renewables_share_energy': 'Renewable Share (%)',
            'co2_per_capita': 'CO₂ per Capita (t)',
            'renewable_share_change': 'Renewable Growth (pp)'
        }
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth',
                 bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter'),
        coloraxis_colorbar=dict(len=0.7, thickness=12, tickfont=dict(size=10),
                                title=dict(text=metric_info['unit'], font=dict(size=11)))
    )
    return fig

@callback(
    Output('map-interval', 'disabled'),
    Output('map-play-btn', 'children'),
    Output('map-playing-state', 'data'),
    Input('map-play-btn', 'n_clicks'),
    State('map-playing-state', 'data')
)
def toggle_map_play(n_clicks, is_playing):
    if n_clicks == 0:
        return True, '▶ Play', False
    if is_playing:
        return True, '▶ Play', False
    return False, '⏸ Pause', True

@callback(
    Output('map-year-slider', 'value'),
    Input('map-interval', 'n_intervals'),
    State('map-year-slider', 'value')
)
def advance_map_year(n_intervals, current_year):
    if current_year >= 2022:
        return 2000
    return current_year + 1
