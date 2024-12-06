## K8s Metrics Collector

This is a simple tool to collect CPU/RAM metrics from a Kubernetes cluster and save them to a local file.

### Usage

Clone the repo and install dependencies:

```bash
uv sync
```

Run the script:

```bash
uv run main.py
```

Open your browser and go to `http://localhost:8050`.

`/timeline` endpoint show mean CPU/RAM changes over time within deployment.
`/cluster_load` endpoint show CPU/RAM usage distribution across pods in one deployment.

### Configuration

Example `config.toml` file is provided in the repo. You can customize it to your needs.

### Limitations

- Refresh time can't be less than callback processing time as `Dash` interval
still triggers callback even if it's already triggered. This cause infinite
loading of the page.
- Dash uses Flask internally, so you might experience issues if you need to deal with async.
- This project lack of configuration as it was initially built for internal use.
- This project is not production ready and primarily intended for personal use.


### Contributing

Feel free to open issues and pull requests if you find any bugs (be sure you will, it was written in 1 day).
