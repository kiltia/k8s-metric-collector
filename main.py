import os
from datetime import datetime

import dash
import pandas as pd
from dash import dcc, html, Dash

from draw import draw_timeline_plot, draw_load_plot, update_timeline_plot
from data import get_actual_data, get_limits, get_raw_limits
from config import config
from io import StringIO

app = Dash(use_pages=True)


app.layout = html.Div(
    [
        dcc.Store(id="data"),
        dcc.Interval(id="interval", interval=config.refresh_interval),
        dash.page_container,
    ]
)


@app.callback(
    dash.dependencies.Output("data", "data"),
    [
        dash.dependencies.Input("interval", "n_intervals"),
        dash.dependencies.State("data", "data"),
    ],
)
def update_data(_, data):
    time = datetime.now()
    new_df = get_actual_data(time)

    if data is None:
        df = (
            pd.read_csv("output.csv")
            if os.path.exists("output.csv")
            else pd.DataFrame()
        )
        limits = get_raw_limits()
        cpu_limits, mem_limits = get_limits(limits, time)
        data = pd.concat([df, new_df, cpu_limits, mem_limits], ignore_index=True)
    else:
        data = pd.read_json(StringIO(data))

    data = pd.concat([data, new_df], ignore_index=True)

    data.to_csv("output.csv", index=False)
    return data.to_json(date_format="iso")


@app.callback(
    dash.dependencies.Output("load_balance", "figure"),
    [
        dash.dependencies.Input("data", "data"),
    ],
)
def update_load_balance(data):
    load_balance = draw_load_plot(pd.read_json(StringIO(data)))
    return load_balance


timeline = None


@app.callback(
    dash.dependencies.Output("timeline", "figure"),
    [
        dash.dependencies.Input("data", "data"),
    ],
)
def update_timeline(data):
    global timeline
    df = pd.read_json(StringIO(data))

    if timeline is None:
        timeline = draw_timeline_plot(df)
        return timeline

    timeline = update_timeline_plot(df, timeline)
    return timeline


if __name__ == "__main__":
    app.run_server(debug=True)
