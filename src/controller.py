import numpy as np
from typing import Dict

class ScalingController:
    def __init__(self, qos_latency_threshold: float, risk_tolerance_alpha: float = 0.95):
        self.qos_threshold = qos_latency_threshold
        # Alpha represents the confidence level (e.g., 95th percentile worst-case risk scaling)
        self.alpha = risk_tolerance_alpha 

    def optimize_allocation(self, predicted_means: np.ndarray, predicted_vars: np.ndarray, current_nodes: int) -> int:
        """
        Evaluates the joint risk profile to determine optimal multi-cloud cluster scaling steps.
        """
        # Calculate the risk-adjusted indicator threshold: Mean + Z*(Standard Deviation)
        # This addresses the JointScaler requirement of factoring in model limitations/uncertainties.
        z_score = 1.645 if self.alpha == 0.95 else 1.96
        risk_adjusted_indicators = predicted_means + z_score * np.sqrt(predicted_vars)
        
        target_cpu_risk = risk_adjusted_indicators[0]
        
        # Resource allocation control laws
        if target_cpu_risk > 0.85:
            # Proactively scale out up to a maximum fleet boundary
            return min(current_nodes + 2, 10)
        elif target_cpu_risk > 0.70:
            return min(current_nodes + 1, 10)
        elif target_cpu_risk < 0.35:
            # Safely scale down to minimize multi-cloud resource spending
            return max(current_nodes - 1, 3)
            
        return current_nodes