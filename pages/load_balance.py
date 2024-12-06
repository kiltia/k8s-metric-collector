import dash
from dash import dcc, html

dash.register_page(__name__, path="/load_balance")

layout = html.Div(
    [
        dcc.Graph(
            id="load_balance",
            style={"width": "100%", "height": "100vh"},
        ),
    ],
)
