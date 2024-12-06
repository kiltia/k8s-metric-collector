import dash
from dash import dcc, html

dash.register_page(__name__, path="/timeline")

layout = html.Div(
    [
        dcc.Graph(
            id="timeline",
            style={"width": "100%", "height": "100vh"},
        ),
    ],
)
