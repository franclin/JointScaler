import simpy
import yaml
import os
from src.telemetry import TelemetryTracker
from src.predictor import JointScalerPredictor
from src.controller import ScalingController
from src.environment import ClusterEnvironment
from src.workload_gen import WorkloadType
from src.dashboard import generate_cluster_dashboard

def load_default_config():
    """Fallback configurations matching MongoDB operational baselines."""
    return {
        "simulation": {
            "duration_ticks": 60,
            "initial_nodes": 3
        },
        "qos": {
            "latency_threshold_ms": 30.0,
            "risk_tolerance_alpha": 0.95
        }
    }

def main():
    print("=" * 70)
    print("JOINTSCALER (IJCAI 2026) INSPIRED CLUSTER SIMULATOR INITIALIZING")
    print("=" * 70)

    # 1. Load Configurations from YAML (Falls back to defaults if missing)
    config = load_default_config()
    config_path = "config/sim_config.yaml"
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)
            if yaml_data:
                # Deep update to merge sub-dictionaries safely
                if "simulation" in yaml_data:
                    config["simulation"].update(yaml_data["simulation"])
                if "qos" in yaml_data:
                    config["qos"].update(yaml_data["qos"])
        print(f"✅ Loaded configuration variables from '{config_path}'")
    else:
        print(f"⚠️ '{config_path}' not found. Utilizing default fallback parameters.")

    # Print out values to terminal so you can verify they are actively being used
    print(f" -> Duration Ticks: {config['simulation']['duration_ticks']}")
    print(f" -> Initial Nodes : {config['simulation']['initial_nodes']}")
    print(f" -> SLA Latency : {config['qos']['latency_threshold_ms']} ms")
    print(f" -> Risk Alpha (Z): {config['qos']['risk_tolerance_alpha']}")
    print("-" * 70)

    # 2. Component Initialization passing the parsed values
    env = simpy.Environment()
    predictor = JointScalerPredictor(lookback_window=10)
    
    # Passing dynamic configuration thresholds to the Controller
    controller = ScalingController(
        qos_latency_threshold=config["qos"]["latency_threshold_ms"],
        risk_tolerance_alpha=config["qos"]["risk_tolerance_alpha"]
    )
    
    cluster_sim = ClusterEnvironment(
        env=env, 
        predictor=predictor, 
        controller=controller, 
        num_tenants=6
    )
    
    # Passing the initial node setup directly to the simulation environment configuration
    cluster_sim.active_nodes = config["simulation"]["initial_nodes"]
    tracker = TelemetryTracker(window_size=60)
    visual_analytics_history = []

    # 3. Scheduled Stress-Test Bottleneck Injections
    def scenario_orchestrator(sim_env, sim_cluster):
        yield sim_env.timeout(10)
        print(f"\n--- [Time {sim_env.now}] Injecting Bottleneck: CONCURRENT READ BURST (Cache Saturated) ---")
        sim_cluster.workload_gen.trigger_bottleneck(WorkloadType.CONCURRENT_READ_BURST, duration=8)
        
        yield sim_env.timeout(20)
        print(f"\n--- [Time {sim_env.now}] Injecting Bottleneck: INDEX BUILD LOCK (Thread Saturation) ---")
        sim_cluster.workload_gen.trigger_bottleneck(WorkloadType.INDEX_BUILD_LOCK, duration=8)

    def analytics_harvest_loop(sim_env, sim_tracker, sim_cluster):
        while True:
            yield sim_env.timeout(1)
            if sim_tracker.history:
                visual_analytics_history.append((sim_tracker.history[-1], sim_cluster.active_nodes))

    # 4. Bind Simulation Process Routines
    env.process(cluster_sim.run_workload_loop(tracker))
    env.process(cluster_sim.run_scaling_loop())
    env.process(scenario_orchestrator(env, cluster_sim))
    env.process(analytics_harvest_loop(env, tracker, cluster_sim))

    # 5. Execute Simulation using dynamic duration parameter
    duration = config["simulation"]["duration_ticks"]
    print(f"Executing event loop for {duration} intervals...")
    env.run(until=duration)

    # 6. Post-Simulation Summary
    print("\n" + "=" * 70)
    print("SIMULATION RUN COMPLETE")
    print("=" * 70)
    print(f"Total Operational Ticks : {duration}")
    print(f"Final Fleet Capacity : {cluster_sim.active_nodes} Nodes")
    print(f"Total Recorded SLA Breaches: {cluster_sim.sla_violations}")
    
    generate_cluster_dashboard(visual_analytics_history, output_filename="cluster_dashboard.html")

if __name__ == "__main__":
    main()