import numpy as np
from dataclasses import dataclass

@dataclass
class TelemetryVector:
    cpu_utilization: float # Percentage (0.0 - 1.0)
    ram_utilization: float # Percentage (0.0 - 1.0)
    disk_io_ops: float # Normalized IOPS
    network_latency: float # Milliseconds

class TelemetryTracker:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.history = []

    def push(self, metrics: TelemetryVector):
        if len(self.history) >= self.window_size:
            self.history.pop(0)
        self.history.append(metrics)

    def get_correlation_matrix(self) -> np.ndarray:
        """Captures the JointScaler multi-indicator dependency mapping."""
        data = np.array([[m.cpu_utilization, m.ram_utilization, m.disk_io_ops] for m in self.history])
        if len(data) < 2:
            return np.eye(3)
        return np.corrcoef(data, rowvar=False)