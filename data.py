import subprocess
import pandas as pd
from utils import parse_cpu, parse_mem
from config import config

metric_columns = ["pod_name", "cpu", "mem", "type", "time"]


def get_raw_metrics() -> str:
    result = subprocess.run(
        config.top_command,
        text=True,
        capture_output=True,
    )

    return result.stdout


def get_raw_limits() -> str:
    result = subprocess.run(
        config.limits_command,
        text=True,
        capture_output=True,
    )

    return result.stdout


def get_df(output: str, columns: list[str]) -> pd.DataFrame:
    records = []
    splitted = output.split("\n")
    columns = columns
    for line in splitted[1:]:
        parts = line.split()
        if len(parts) == 0:
            continue
        parts = parts
        d = {k: v for k, v in zip(columns, parts)}
        records.append(d)

    df = pd.DataFrame(records, columns=columns)

    def convert_name(pod_name: str) -> str:
        splitted = pod_name.split("-")
        if len(splitted) < 3:
            return pod_name
        else:
            return "-".join(splitted[:-2])

    df["pod_name"] = df["pod_name"].apply(convert_name)
    return df


def get_metrics(output: str, columns: list[str], time) -> pd.DataFrame:
    df = get_df(output, metric_columns[:-1])
    df["time"] = time
    df["cpu"] = df["cpu"].apply(parse_cpu)
    df["mem"] = df["mem"].apply(parse_mem)
    df["type"] = "usage"
    return df


def get_limits(output: str, time) -> pd.DataFrame:
    limits_columns = ["pod_name", "cpu_req", "cpu_lim", "mem_req", "mem_lim"]
    df = get_df(output, limits_columns)
    df["cpu_req"] = df["cpu_req"].apply(parse_cpu)
    df["cpu_lim"] = df["cpu_lim"].apply(parse_cpu)
    df["mem_req"] = df["mem_req"].apply(parse_mem)
    df["mem_lim"] = df["mem_lim"].apply(parse_mem)

    df["type"] = ""
    df["time"] = time

    df_req = df[["pod_name", "cpu_req", "mem_req", "type", "time"]].copy()
    df_lim = df[["pod_name", "cpu_lim", "mem_lim", "type", "time"]].copy()

    df_req["type"] = "requests"
    df_lim["type"] = "limits"

    df_req.columns = metric_columns
    df_lim.columns = metric_columns

    return df_req, df_lim


def get_actual_data(time) -> pd.DataFrame:
    metric_output = get_raw_metrics()
    metric_df = get_metrics(metric_output, metric_columns, time)

    return metric_df
