from .callbacks import init_callbacks
from dash import Dash, html
from .layout import layout


def init_dashboard(app, path: str = '/dash/', layout: "html" = layout):
    dash_app = Dash(
        server=app,
        routes_pathname_prefix=path
    )

    dash_app.layout = layout

    dash_app = init_callbacks(dash_app)

    # Dash html to file for reach another file
    with open('interface/templates/dash_raw.html', 'w') as file:
        file.writelines(dash_app.index())

    return dash_app.server
