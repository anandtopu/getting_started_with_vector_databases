"""Sample process RSS during a measured section, rather than mistaking Python heap for RAM."""

import threading
from pathlib import Path

import psutil


class MemorySampler:
    def __init__(self, interval: float = 0.01) -> None:
        self.interval = interval
        self.process = psutil.Process()
        self.baseline = self.process.memory_info().rss
        self.peak = self.baseline
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self._stop.wait(self.interval):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.peak = max(self.peak, self.process.memory_info().rss)
        self._stop.set()
        self._thread.join()

    def report(self) -> dict:
        return {
            "process_baseline_rss_bytes": self.baseline,
            "process_peak_rss_bytes": self.peak,
            "process_peak_delta_bytes": self.peak - self.baseline,
            "rss_sampling_interval_seconds": self.interval,
            "server_memory_bytes": None,
            "server_memory_reason": "in-process backend; no separate server",
            "limitations": "Sampled RSS may miss peaks shorter than the sampling interval; includes interpreter and imported libraries.",
        }


def disk_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
