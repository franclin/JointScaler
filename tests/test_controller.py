import pytest
import numpy as np
from src.controller import ScalingController

@pytest.fixture
def controller():
    """Initializes the policy controller with a 30ms threshold and 95% risk bounds."""
    return ScalingController(qos_latency_threshold=30.0, risk_tolerance_alpha=0.95)

def test_steady_state_no_scaling(controller):
    """Ensures that when predicted metrics are low and stable, the cluster pool remains steady."""
    predicted_means = np.array([0.4, 0.4, 300.0]) # Stable indicators well below threshold
    predicted_vars = np.array([0.001, 0.001, 5.0]) # Minimal uncertainty bounds
    
    # Executing policy evaluation with an initial pool of 4 nodes
    calculated_nodes = controller.optimize_allocation(predicted_means, predicted_vars, current_nodes=4)
    
    assert calculated_nodes == 4 # Should not trigger an unnecessary adjustment

def test_proactive_scaling_due_to_high_uncertainty(controller):
    """
    Verifies the core JointScaler objective: Even if the predicted mean is moderate,
    a high variance (uncertainty spike) must force the controller to scale out early.
    """
    predicted_means = np.array([0.65, 0.50, 400.0]) # Means look moderately safe (< 0.70)
    high_variance = np.array([0.15, 0.01, 10.0]) # Massive CPU prediction volatility spike
    
    calculated_nodes = controller.optimize_allocation(predicted_means, high_variance, current_nodes=4)
    
    # Mean (0.65) + Z*(sqrt(0.15)) shifts the risk-adjusted value past the 0.85 threshold.
    # Therefore, the controller must aggressively scale out to buffer against the risk.
    assert calculated_nodes > 4

def test_safe_scale_down(controller):
    """Ensures that when the cluster is massively over-provisioned, it steps down safely."""
    predicted_means = np.array([0.2, 0.2, 50.0]) # Idle server metrics
    predicted_vars = np.array([0.001, 0.001, 1.0]) # Confident predictions
    
    calculated_nodes = controller.optimize_allocation(predicted_means, predicted_vars, current_nodes=8)
    
    assert calculated_nodes == 7 # Consolidation scaling step down should execute safely