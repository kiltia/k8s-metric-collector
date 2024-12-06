from pydantic import BaseModel
import tomllib


class Config(BaseModel):
    top_command: list[str] = ["kubectl", "top", "pod"]
    limits_command: list[str] = [
        "kubectl",
        "get",
        "pods",
        "-o",
        "custom-columns='NAME:.metadata.name,CPU_REQ:spec.containers[].resources.requests.cpu,CPU_LIM:spec.containers[].resources.limits.cpu,MEMORY_REQ:spec.containers[].resources.requests.memory,MEM_LIM:spec.containers[].resources.limits.memory'",
    ]
    refresh_interval: int = 2000  # ms


with open("config.toml", "rb") as f:
    data = tomllib.load(f)

config = Config.model_validate(data)
