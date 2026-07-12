# =============================================================================
# CS661 Group 4 — Global Energy Transition Web App
# Sidebar-navigated, full-viewport, warm amber theme
# Modular Entry Point
# =============================================================================

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx

from data_loader import all_countries
from config import PAGES, DEFAULT_COUNTRIES
from pages import map_page, stream_page, index_page, bubble_page, parallel_page, radar_page

# Initialize Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "Global Energy Transition | CS661 Group 4"

# Sidebar builder
def build_sidebar():
    nav_items = []
    for page in PAGES:
        nav_items.append(
            html.Button(
                [
                    html.Span(page['icon'], className='nav-icon'),
                    html.Span([
                        html.Span(page['label'], className='nav-label'),
                        html.Span(page['short'], className='nav-short'),
                    ], className='nav-label-wrap')
                ],
                id=page['nav_id'],
                className='nav-item-btn active' if page['id'] == 'page-map' else 'nav-item-btn',
                n_clicks=0
            )
        )

    return html.Div([
        # Brand
        html.Div([
            html.Span('🌍', id='brand-globe'),
            html.Div('Global Energy Transition', id='brand-title'),
            html.Div('CS661 · Group 4', id='brand-sub'),
        ], id='sidebar-brand'),

        # Nav
        html.Div(nav_items, id='sidebar-nav'),

        # Controls section (scrollable)
        html.Div([
            # Country selector
            html.Div([
                html.Span('Compare Countries', className='sidebar-section-label'),
                dcc.Dropdown(
                    id='global-country-dropdown',
                    options=[{'label': c, 'value': c} for c in all_countries],
                    value=DEFAULT_COUNTRIES,
                    multi=True,
                    placeholder='Select countries…',
                    style={'fontSize': '11px'}
                )
            ], className='sidebar-section'),
        ], id='sidebar-controls'),

        # Footer
        html.Div([
            html.P('OWID Energy Dataset · 2000–2022')
        ], id='sidebar-footer'),

        # Toggle button
        html.Button('◀', id='sidebar-toggle', n_clicks=0),

    ], id='sidebar')

# Master Layout
app.layout = html.Div([
    # Hidden state stores
    dcc.Store(id='active-page', data='page-map'),
    dcc.Store(id='sidebar-collapsed', data=False),
    dcc.Store(id='map-playing-state', data=False),
    dcc.Interval(id='map-interval', interval=800, disabled=True),
    dcc.Store(id='bubble-reset-counter', data=0),
    dcc.Store(id='bubble-clicked-country', data=None),
    dcc.Store(id='parallel-reset-counter', data=0),

    # App shell
    html.Div([
        build_sidebar(),

        # Content area
        html.Div([
            html.Div([
                map_page.layout,
                stream_page.layout,
                index_page.layout,
                bubble_page.layout,
                parallel_page.layout,
                radar_page.layout
            ], id='content-area')
        ], id='main-area')

    ], id='app-shell')
])

# ── Sidebar collapse callback ──
@app.callback(
    Output('sidebar', 'className'),
    Output('sidebar-collapsed', 'data'),
    Output('sidebar-toggle', 'children'),
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar-collapsed', 'data')
)
def toggle_sidebar(n_clicks, is_collapsed):
    if n_clicks == 0:
        return '', False, '◀'
    new_state = not is_collapsed
    if new_state:
        return 'collapsed', True, '◀'
    return '', False, '◀'

# ── Page routing: update active page store ──
nav_inputs = [Input(page['nav_id'], 'n_clicks') for page in PAGES]

@app.callback(
    Output('active-page', 'data'),
    *nav_inputs
)
def route_page(*args):
    triggered = ctx.triggered_id
    if triggered is None:
        return 'page-map'
    id_to_page = {page['nav_id']: page['id'] for page in PAGES}
    return id_to_page.get(triggered, 'page-map')

# ── Page routing: show/hide panels + update nav button classes ──
page_outputs = [Output(page['id'], 'className') for page in PAGES]
nav_outputs  = [Output(page['nav_id'], 'className') for page in PAGES]

@app.callback(
    *page_outputs,
    *nav_outputs,
    Input('active-page', 'data')
)
def show_hide_pages(active_page):
    page_classes = []
    nav_classes = []
    for page in PAGES:
        if page['id'] == active_page:
            page_classes.append('page-panel active')
            nav_classes.append('nav-item-btn active')
        else:
            page_classes.append('page-panel')
            nav_classes.append('nav-item-btn')
    return *page_classes, *nav_classes

if __name__ == '__main__':
    app.run(debug=True)
