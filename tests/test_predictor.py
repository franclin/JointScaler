import pytest
import numpy as np
from src.telemetry import TelemetryVector
from src.predictor import JointScalerPredictor

@pytest.fixture
def predictor():
    """Initializes the predictor with a 10-tick lookback window."""
    return JointScalerPredictor(lookback_window=10)

def test_cold_start_fallback(predictor):
    """
    Ensures that when telemetry history is shorter than the lookback window,
    the predictor returns a safe, un-infinite default baseline configuration.
    """
    short_history = [
        TelemetryVector(cpu_utilization=0.4, ram_utilization=0.4, disk_io_ops=200, network_latency=5.0)
    ]
    
    means, variances = predictor.predict_next_step_distribution(short_history)
    
    # Assert fallback averages are executed safely
    assert isinstance(means, np.ndarray)
    assert isinstance(variances, np.ndarray)
    assert means.shape == (3,)
    assert variances.shape == (3,)
    assert np.all(means == 0.5)

def test_zero_variance_stream(predictor):
    """
    Tests that a perfectly uniform telemetry stream doesn't trigger 
    divide-by-zero or vanishing variance numerical errors.
    """
    # Create a completely flat history longer than the lookback window
    flat_history = [
        TelemetryVector(cpu_utilization=0.5, ram_utilization=0.6, disk_io_ops=500.0, network_latency=10.0)
        for _ in range(12)
    ]
    
    means, variances = predictor.predict_next_step_distribution(flat_history)
    
    # Check that means match input metrics exactly
    assert pytest.approx(means[0]) == 0.5
    assert pytest.approx(means[1]) == 0.6
    
    # Ensure regularizer (1e-4) prevents variance from hitting exactly absolute zero
    assert np.all(variances > 0.0)
    assert np.all(variances >= 1e-4)

def test_uncertainty_tracking_under_volatility(predictor):
    """
    Verifies that highly volatile metric streams translate into higher
    predictive uncertainty (variance), a key element of the JointScaler approach.
    """
    # Stream A: Stable baseline operations
    stable_history = [
        TelemetryVector(cpu_utilization=0.4 + (i % 2) * 0.02, ram_utilization=0.5, disk_io_ops=100, network_latency=5.0)
        for i in range(12)
    ]
    
    # Stream B: Highly volatile workload spike (simulating a database bottleneck)
    volatile_history = [
        TelemetryVector(cpu_utilization=0.4 if i < 6 else 0.9, ram_utilization=0.5, disk_io_ops=100, network_latency=5.0)
        for i in range(12)
    ]
    
    _, stable_vars = predictor.predict_next_step_distribution(stable_history)
    _, volatile_vars = predictor.predict_next_step_distribution(volatile_history)
    
    # The CPU variance indicator (index 0) must reflect the volatility drop/spike accurately
    assert volatile_vars[0] > stable_vars[0]