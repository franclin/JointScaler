import simpy
from src.telemetry import TelemetryVector
from src.workload_gen import MultiTenantWorkloadGenerator, WorkloadType

class ClusterEnvironment:
    def __init__(self, env: simpy.Environment, predictor, controller, num_tenants: int = 8):
        self.env = env
        self.predictor = predictor
        self.controller = controller
        self.tracker = None # Instantiated in main execution loop
        self.workload_gen = MultiTenantWorkloadGenerator(num_tenants=num_tenants)
        self.active_nodes = 3 # Initial cluster baseline capacity
        self.sla_violations = 0

    def run_workload_loop(self, tracker):
        """Simulates incoming concurrent multi-tenant database traffic streams."""
        self.tracker = tracker
        while True:
            # Generate metrics taking active capacity boundaries into account
            metrics = self.workload_gen.generate_next_metrics(self.active_nodes, self.env.now)
            
            vector = TelemetryVector(
                cpu_utilization=metrics["cpu"],
                ram_utilization=metrics["ram"],
                disk_io_ops=metrics["io"],
                network_latency=metrics["latency"]
            )
            
            self.tracker.push(vector)
            
            # Track SLA drops (e.g., latency spikes past MongoDB's standard 30ms operational target)
            # replace with self.controller.qos_latency_threshold
            if vector.network_latency > 30.0:
                self.sla_violations += 1
                print(f"[🚨 SLA BREACH - Time {self.env.now:.1f}] Latency at {vector.network_latency:.1f}ms! "
                      f"State: {metrics['active_bottleneck']} | Active Nodes: {self.active_nodes}")

            yield self.env.timeout(1) # Tick step (e.g., 1-minute window telemetry aggregation)

    def run_scaling_loop(self):
        """Runs the JointScaler uncertainty-aware policy appraisal window."""
        while True:
            # Evaluate scaling decisions at a slightly slower horizon (every 5 ticks)
            # to mimic realistic infrastructure cooldown allocations
            yield self.env.timeout(5)
            
            if self.tracker and self.tracker.history:
                # Extract mean and uncertainty variance from our core JointScaler predictor
                means, variances = self.predictor.predict_next_step_distribution(self.tracker.history)
                
                # Command our controller to compute the optimal node allocation pool
                new_node_count = self.controller.optimize_allocation(means, variances, self.active_nodes)
                
                if new_node_count != self.active_nodes:
                    print(f"🎛️ [Time {self.env.now:.1f}] Policy Action: Cluster scaled from {self.active_nodes} to {new_node_count} nodes.")
                    self.active_nodes = new_node_count