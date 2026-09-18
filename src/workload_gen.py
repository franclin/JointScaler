import random
from enum import Enum
from dataclasses import dataclass

class WorkloadType(Enum):
    CONCURRENT_READ_BURST = "concurrent_read_burst" # Spikes RAM cache and network latency
    INDEX_BUILD_LOCK = "index_build_lock" # Spikes CPU and Disk I/O, blocks execution
    BULK_WRITE_INGESTION = "bulk_write_ingestion" # Sustained Disk I/O and moderate CPU
    STEADY_STATE = "steady_state" # Baseline operational telemetry

@dataclass
class TenantProfile:
    tenant_id: str
    tier: str # "premium" (SLA guaranteed) or "free-tier" (noisy neighbor)
    base_query_rate: float # Queries per second baseline

class MultiTenantWorkloadGenerator:
    def __init__(self, num_tenants: int = 5):
        self.tenants = [
            TenantProfile(tenant_id=f"tenant_{i}", tier="premium" if i % 2 == 0 else "free-tier", base_query_rate=random.uniform(10, 50))
            for i in range(num_tenants)
        ]
        self.current_anomaly = WorkloadType.STEADY_STATE
        self.anomaly_duration_remaining = 0

    def trigger_bottleneck(self, bottleneck_type: WorkloadType, duration: int):
        """Manually injects a specific infrastructure bottleneck pattern."""
        self.current_anomaly = bottleneck_type
        self.anomaly_duration_remaining = duration

    def generate_next_metrics(self, current_nodes: int, sim_time: float) -> dict:
        """
        Generates the raw workload demand factors matching specific bottleneck states.
        Balances premium tenant isolation against free-tier 'noisy neighbor' spikes.
        """
        # 1. Establish underlying baseline demand
        total_qps = sum(t.base_query_rate for t in self.tenants)
        
        # Inject standard time-of-day business cycle oscillations
        time_factor = 1.5 if (sim_time % 24) >= 9 and (sim_time % 24) <= 18 else 0.5
        total_qps *= time_factor

        # 2. Initialize raw demand vectors before cluster node mitigation
        raw_cpu_demand = (total_qps * 0.005)
        raw_ram_demand = (total_qps * 0.008)
        raw_io_demand = (total_qps * 2.0)
        
        # 3. Apply Bottleneck Modifiers (The core simulation states)
        if self.anomaly_duration_remaining > 0:
            self.anomaly_duration_remaining -= 1
            
            if self.current_anomaly == WorkloadType.CONCURRENT_READ_BURST:
                # Cache misses push index searches heavily into memory pools
                raw_ram_demand *= 4.5
                raw_cpu_demand *= 1.8
                raw_io_demand *= 1.2
                
            elif self.current_anomaly == WorkloadType.INDEX_BUILD_LOCK:
                # Foreground index locks paralyze a collection, maxing out core execution threads
                raw_cpu_demand *= 6.0
                raw_io_demand *= 5.0
                raw_ram_demand *= 1.1 # Minimal cache interaction
                
            elif self.current_anomaly == WorkloadType.BULK_WRITE_INGESTION:
                # Heavy inserts trigger write-ahead log (WAL) flushes and disk saturation
                raw_io_demand *= 8.0
                raw_cpu_demand *= 2.5
                raw_ram_demand *= 2.0
        else:
            self.current_anomaly = WorkloadType.STEADY_STATE
            # 5% chance an unmanaged "noisy neighbor" free-tier tenant starts a massive unindexed query
            if random.random() < 0.05:
                self.trigger_bottleneck(random.choice([w for w in WorkloadType if w != WorkloadType.STEADY_STATE]), duration=6)

        # 4. Normalize the raw demand by dividing across the cluster's active capacity
        # This mirrors a distributed multi-cloud environment like MongoDB Atlas
        scaled_cpu = min(max(raw_cpu_demand / current_nodes, 0.05), 1.0)
        scaled_ram = min(max(raw_ram_demand / current_nodes, 0.10), 1.0)
        scaled_io = raw_io_demand / current_nodes
        
        # Compute network latency degradation non-linearly if CPU or RAM saturate
        saturation_multiplier = 1.0
        if scaled_cpu > 0.85 or scaled_ram > 0.85:
            saturation_multiplier = 4.5 # Emulates queue pooling timeouts
            
        latency = (5.0 * (scaled_cpu * 1.5) + (scaled_io * 0.002)) * saturation_multiplier

        return {
            "cpu": scaled_cpu,
            "ram": scaled_ram,
            "io": scaled_io,
            "latency": latency,
            "active_bottleneck": self.current_anomaly.value
        }