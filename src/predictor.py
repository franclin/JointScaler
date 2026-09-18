import numpy as np
import scipy.stats as stats
from typing import Tuple, List
from src.telemetry import TelemetryVector

class JointScalerPredictor:
    def __init__(self, lookback_window: int = 15):
        self.lookback_window = lookback_window

    def predict_next_step_distribution(self, history: List[TelemetryVector]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Mimics JointScaler's probabilistic forecasting.
        Returns:
            means: array of predicted mean states [E(CPU), E(RAM), E(IO)]
            variances: array of uncertainties (variance) representing model confidence
        """
        if len(history) < self.lookback_window:
            # Fallback to moving baseline if history is warm
            return np.array([0.5, 0.5, 0.5]), np.array([0.05, 0.05, 0.05])
        
        # Extract recent vector windows
        cpu_data = [m.cpu_utilization for m in history[-self.lookback_window:]]
        ram_data = [m.ram_utilization for m in history[-self.lookback_window:]]
        io_data = [m.disk_io_ops for m in history[-self.lookback_window:]]

        # In production, this would leverage normalizing flows or a probabilistic model.
        # For simulation, we compute a Gaussian predictive distribution based on historical trend volatility.
        means = np.array([np.mean(cpu_data), np.mean(ram_data), np.mean(io_data)])
        variances = np.array([np.var(cpu_data), np.var(ram_data), np.var(io_data)]) + 1e-4

        return means, variances