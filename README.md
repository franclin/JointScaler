# JointScaler: Uncertainty-Aware Infrastructure Auto-Scaling Engine

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Docker Compliant](https://img.shields.io/badge/container-docker-blue)](https://www.docker.com/)
[![Testing Framework](https://img.shields.io/badge/test-pytest-green)](https://docs.pytest.org/)

An event-driven simulation platform implementing an uncertainty-aware infrastructure auto-scaler inspired by the **[JointScaler (IJCAI 2026)] (https://www.ijcai.org/proceedings/2026/323)** architectural framework. This repository models multi-tenant database workload constraints, tracks multi-indicator telemetry correlations, and uses probabilistic statistical distribution bounds to dynamically scale cluster fleets ahead of QoS degradations.

This engine is built specifically to demonstrate production-grade software architecture integrated directly with rigorous applied statistical workflows—bridging the gap between distributed infrastructure engineering and operational machine learning.

---

## 🏗️ Architectural Overview & Design Patterns

The project follows strict **object-oriented programming (OOP)** principles and an event-driven design pattern to simulate a real-world cloud fleet cluster ecosystem (such as MongoDB Atlas).

```text
                           [ Multi-Tenant Workload Generator ]
                                            │ 
                                   Spikes & Bottlenecks
                                            ▼
[ Controller Action ] ──► [ SimPy Event-Driven Cluster Env ] ──► [ Telemetry Tracker ]
  Scales Fleet Pool          (Calculates Capacity Saturation)        Bundles State Vectors
         ▲                                                                  │
         │                                                                  ▼
         └───────────── [ Uncertainty-Aware Predictor ] ◄───────────────────┘
                           Computes Mean + Variance Risk
```

*   **Event-Driven Environment (`src/environment.py`):** Leverages `SimPy` to orchestrate discrete time-step simulations without resource-heavy loop configurations.
*   **Multi-Indicator Tracking (`src/telemetry.py`):** Bundles concurrent system performance metrics (CPU, RAM, Disk I/O, Network Latency) into cohesive state vectors rather than evaluating metrics in isolation.
*   **Decoupled Policy Controller (`src/controller.py`):** Isolates the statistical threshold decision matrix from simulation states, making the deployment logic highly testable.

---

## 📊 Core Statistical Foundations (JointScaler IJCAI 2026)

Traditional auto-scalers react blindly to isolated metric thresholds (e.g., *scale if CPU > 80%*). This engine addresses those limitations by injecting two principles from the JointScaler paper:

### 1. Multi-Indicator Dependency Mapping
Database infrastructure failure states are rarely driven by a single independent variable. An index build paralyzes CPU and Disk I/O concurrently, while a read-heavy query burst shifts cache hits into memory pools. 
The system continuously tracks a sliding rolling window of telemetry arrays to output a real-time **Pearson Correlation Matrix ($R$)** across indicators:

$$R_{X,Y} = \frac{\mathop{\text{cov}}(X,Y)}{\sigma_X \sigma_Y}$$

This captures hidden, structural system dependencies across separate resource pools before scaling actions are committed.

### 2. Uncertainty-Aware / Probabilistic Control Loops
Machine learning models are inherently limited by telemetry noise and distribution shifts. To safeguard fleet stability, the prediction layer returns a **Gaussian Predictive Distribution** parameterized by a mean ($\mu$) and variance ($\sigma^2$) vector rather than a deterministic point estimate.

The controller evaluates allocation requirements against a **Risk-Adjusted Scaling Target** leveraging the 95th Percentile ($Z = 1.645$) boundary:

$$\text{Target Resource Risk} = \mu_{\text{indicator}} + (Z_{\alpha} \times \sqrt{\sigma^2_{\text{indicator}}})$$

*   **Low Uncertainty (Small Variance):** The control policy relies safely on the projected baseline path.
*   **High Uncertainty (Large Volatility Spikes):** The variance expansion scales the risk target upward proactively. This triggers protective "scale-out" operations early, mitigating worst-case SLA degradations.

---

## 🔍 Simulated Database Bottlenecks

The workload generator avoids generic synthetic noise to emulate authentic distributed database contention bottlenecks:

1.  **`CONCURRENT_READ_BURST`:** Simulates heavy client reads causing memory cache misses. This pushes cache indexing into memory pools, driving sharp RAM saturation along with minor CPU escalations.
2.  **`INDEX_BUILD_LOCK`:** Simulates an unoptimized, foreground database collection index execution. This locks operational threads, triggering massive CPU and Disk I/O utilization spikes.
3.  **`BULK_WRITE_INGESTION`:** Simulates high-throughput document insert pipelines. This triggers intensive write-ahead logging (WAL) flushes, saturating underlying disk operations.

---

## 🚀 Quick Start & Container Execution

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and actively running.

### 1. Build the Portability Container Image
Compile the isolated Python runtime and install pinned dependencies cleanly using the Dockerfile:
```bash
docker build -t jointscaler-sim:latest .
```

### 2. Run the Main Simulation Engine
Execute the 60-interval stress-test scenario orchestrator directly inside your terminal shell:
```bash
docker run --rm --name telemetry-simulation jointscaler:latest
```

### 3. Run the Automated Test Suite (`pytest`)
Validate the model's cold-start parameters, zero-variance boundaries, and uncertainty tracking thresholds via the container footprint:
```bash
docker run --rm jointscaler:latest python -m pytest tests/
```

### 4. Extract the Interactive Plotly Analytics Dashboard
To view the full visual loop output on your local machine, run the engine with a volume bind mount to dump the compiled dashboard report:
```bash
docker run --rm -v "$(pwd)":/app/output jointscaler:latest python main.py
```
*(Open the resulting `output/cluster_dashboard.html` file inside any standard web browser to interactively trace utilization profiles vs. proactive fleet scaling timelines).*

OR
Run the simulation to explicitly generate the HTML asset
```bash
docker run --name simulation-runner jointscaler:latest python main.py
```

Then Copy the generated file straight to your Computer
```bash
docker cp simulation-runner:/app/cluster_dashboard.html ./cluster_dashboard.html
```
Open the HTML file directly in your favourite browser
```bash
open cluster_dashboard.html
```

Finally clear up
```bash
docker rm simulation-runner
docker rm temp-dash
```

---

## 🛠️ Production Verification & Model Limitations

In compliance with professional applied data science engineering practices, this architecture addresses specific boundary conditions and structural model constraints:

*   **Numerical Stability Regularization:** In uniform, static system states where volatility approaches zero ($\sigma^2 \rightarrow 0$), traditional Gaussian evaluation risks division-by-zero runtime panic. This framework integrates a strict regularizing value modifier (+1e-4) to guarantee mathematical continuity across flat baselines.
*   **System Cold-Starts:** If the infrastructure metrics logging history is smaller than the predictor's mandatory lookback window ($t < t_{	ext{lookback}}$), the model drops back to an un-infinite, highly stable 0.5 moving baseline fallback profile to avoid erratic initial cluster thrashing.
*   **Predictor Horizon Bounds:** The current probabilistic simulation layer assumes a localized Gaussian distribution path over short execution steps. Under permanent structural regime shifts (e.g., permanent infrastructure hardware changes), a transformer-based normalizing flow model would be required to maintain long-tail predictive coverage.


## Reference Paper

 - [JointScaler: A Hierarchical Multi-Indicator Distribution Forecasting Approach for Uncertainty-Aware Joint Scaling in Cloud Services] (https://www.ijcai.org/proceedings/2026/323) Published in the Proceedings of the Thirty-Fifth International Joint Conference on Artificial Intelligence Main Track. Pages 2906-2914