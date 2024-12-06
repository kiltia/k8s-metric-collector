import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def update_timeline_plot(df, fig):
    df = df.groupby(["pod_name", "type", "time"]).mean().reset_index()

    def update_trace(trace, metric):
        pod = trace.name.split(":")[0]

        trace.update(
            x=df[(df["type"] == "usage") & (df["pod_name"] == pod)]["time"],
            y=df[(df["type"] == "usage") & (df["pod_name"] == pod)][metric],
            connectgaps=False,
        )

    fig = fig.for_each_trace(lambda trace: update_trace(trace, "cpu"), row=1, col=1)
    fig = fig.for_each_trace(lambda trace: update_trace(trace, "mem"), row=2, col=1)
    return fig


def get_colors():
    import plotly

    hex_colors_only = []
    for hex in plotly.colors.qualitative.Pastel:
        hex_colors_only.append(hex)
    return hex_colors_only


def draw_timeline_plot(df: pd.DataFrame) -> go.Figure:
    df = df.groupby(["pod_name", "type", "time"]).mean().reset_index()
    colors = get_colors()
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, subplot_titles=("CPU", "Memory")
    )
    incr = 0
    requests = df[df["type"] == "requests"]
    limits = df[df["type"] == "limits"]

    for pod in df["pod_name"].unique():
        row = 1
        for metric in ["cpu", "mem"]:
            metric_limit = limits[limits["pod_name"] == pod][metric].iloc[-1]
            metric_request = requests[requests["pod_name"] == pod][metric].iloc[-1]
            suffix = " m" if metric == "cpu" else " Gb"
            fig.add_trace(
                go.Scatter(
                    x=df[df["type"] == "usage"]["time"],
                    y=df[df["type"] == "usage"][metric],
                    name=f"{pod}",
                    line=dict(color=colors[incr]),
                    mode="lines+markers",
                    showlegend=row == 1,
                    visible="legendonly",
                    legendgroup=f"{pod}",
                    hovertemplate="%{y}" + suffix,
                    connectgaps=False,
                ),
                row=row,
                col=1,
            )
            fig.add_hline(
                y=metric_limit,
                line=dict(color=colors[incr], dash="dash"),
                row=row,
                col=1,
            )
            fig.add_hline(
                y=metric_limit / metric_request,
                line=dict(color=colors[incr], dash="dot"),
                row=row,
                col=1,
            )
            row += 1
        incr += 1

    fig.update_xaxes(title_text="Timestamp")
    fig.update_yaxes(title_text="CPU usage (m, mean)", row=1, col=1)
    fig.update_yaxes(title_text="Memory usage (Gb, mean)", row=2, col=1)

    fig.update_layout(uirevision="constant")
    fig.update_layout(hovermode="x unified")

    return fig


def preprocess_load_data(df: pd.DataFrame) -> pd.DataFrame:
    def process_metric(metric, requests):
        def f(x):
            return (
                x[metric]
                / requests[requests["pod_name"] == x["pod_name"]][metric].iloc[-1]
            )

        return f

    df["time"] = pd.to_datetime(df["time"], format="ISO8601")
    usage = df[(df["time"] == df["time"].max()) & (df["type"] == "usage")].copy()
    requests = df[df["type"] == "requests"]
    limits = df[df["type"] == "limits"]
    usage["cpu"] = usage.apply(process_metric("cpu", requests), axis=1)
    usage["mem"] = usage.apply(process_metric("mem", requests), axis=1)

    return usage, requests, limits


def draw_load_plot(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, subplot_titles=("CPU", "Memory")
    )

    usage, requests, limits = preprocess_load_data(df)
    incr = 0

    colors = get_colors()

    for pod in usage["pod_name"].unique():
        row = 1
        request_pod_data = requests[requests["pod_name"] == pod]
        limits_pod_data = limits[limits["pod_name"] == pod]
        for metric in ["cpu", "mem"]:
            metric_request = request_pod_data[metric].iloc[-1]
            metric_limit = limits_pod_data[metric].iloc[-1]
            if row == 1:
                showlegend = True
            else:
                showlegend = False
            points = zip(
                usage[usage["pod_name"] == pod][metric],
                usage[usage["pod_name"] == pod]["time"],
            )
            points = sorted(points, key=lambda x: x[1])

            fig.add_trace(
                go.Histogram(
                    x=usage[usage["pod_name"] == pod][metric],
                    name=pod,
                    showlegend=showlegend,
                    legendgroup=f"{pod}",
                    marker=dict(color=colors[incr]),
                    hovertemplate="%{y} pods between %{x}",
                ),
                row=row,
                col=1,
            )
            if metric_limit != 0:
                fig.add_vline(
                    x=metric_limit / metric_request,
                    line=dict(color=colors[incr], dash="dash"),
                    row=row,
                    col=1,
                )
            row += 1
        incr += 1

    fig.add_vline(
        x=1,
        line=dict(color="gray", dash="dash"),
        row=1,
        col=1,
    )

    fig.add_vline(
        x=1,
        line=dict(color="gray", dash="dash"),
        row=2,
        col=1,
    )

    fig.update_layout(uirevision="constant")
    fig.update_layout(hovermode="x")
    fig.update_xaxes(title_text="CPU usage (% of request)")
    fig.update_yaxes(title_text="Count", range=[0, 15])
    fig.update_xaxes(title_text="Memory usage (% of request)", row=2, col=1)
    return fig
