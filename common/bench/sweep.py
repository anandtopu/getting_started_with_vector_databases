"""Cartesian parameter sweeps use the same runner and store all configurations."""

from itertools import product

from common.bench.config import BenchConfig


def expand_sweep(base: BenchConfig, grid: dict[str, list]) -> list[BenchConfig]:
    if any(not values for values in grid.values()):
        raise ValueError("Sweep values must not be empty")
    configs = []
    keys = list(grid)
    for i, values in enumerate(product(*(grid[key] for key in keys))):
        config = base.model_dump()
        config["parameters"] = dict(base.parameters)
        for key, value in zip(keys, values, strict=True):
            if key.startswith("parameters."):
                config["parameters"][key.split(".", 1)[1]] = value
            elif key in config:
                config[key] = value
            else:
                raise ValueError(f"Unknown sweep setting: {key}")
        config["name"] = f"{base.name}-{i:03d}"
        configs.append(BenchConfig.model_validate(config))
    return configs
