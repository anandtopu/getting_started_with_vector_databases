"""Apply this module to Marlowe seller inventory.
Run: uv run python modules/22_performance/use_case/marlowe.py
CPU: seconds; frozen fixtures only, no model downloads or services.
"""

from common.ops.capacity import estimate, monthly_cost


def main():
    for replicas in [1, 2]:
        for width in [4, 1]:
            plan = estimate(
                rows=10_000_000, dimensions=768, bytes_per_value=width, replicas=replicas
            )
            print(
                "Bytes per value",
                width,
                "replicas",
                replicas,
                "provisioned GiB",
                round(plan["provisioned_bytes"] / 2**30, 2),
            )
    for name, rate, hours in [("self-hosted", 0.5, 8), ("managed", 1.2, 2)]:
        costs = monthly_cost(
            hourly_compute=rate,
            storage_gib=100,
            storage_rate=0.1,
            operator_hours=hours,
            operator_rate=75,
        )
        print(name, costs, sum(costs.values()))
    print(
        "Illustrative prices only. A small immutable catalog may use exact local search with no server."
    )


if __name__ == "__main__":
    main()
