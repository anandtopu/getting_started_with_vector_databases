"""Compare capacity, cost and replica consistency assumptions.
Run: uv run python modules/22_performance/examples/01_from_scratch.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

from common.ops.capacity import estimate, monthly_cost
from common.ops.replication import ReplicaSimulation, shard_for


def main():
    for width in [4, 2, 1]:
        print(width, estimate(bytes_per_value=width, replicas=2))
    replicas = ReplicaSimulation()
    replicas.write("listing", "new price", acknowledgements=1)
    assert replicas.read(2, "listing") is None
    replicas.tick()
    assert replicas.read(2, "listing")[1] == "new price"
    replicas.alive = {0}
    try:
        replicas.write("listing", "later price", acknowledgements=2)
    except RuntimeError:
        print("Quorum unavailable: simulator, not a measured server outage")
    print("Shard routing:", [shard_for(str(i), 4) for i in range(12)])
    for hourly, hours in [(0.5, 8), (1.2, 2)]:
        parts = monthly_cost(
            hourly_compute=hourly,
            storage_gib=100,
            storage_rate=0.1,
            operator_hours=hours,
            operator_rate=75,
        )
        print("Hypothetical USD, not vendor prices:", parts, "total", sum(parts.values()))


if __name__ == "__main__":
    main()
