import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_cluster_dashboard(history_logs: list, output_filename: str = "cluster_dashboard.html"):
    """
    Generates an interactive multi-panel engineering dashboard reflecting 
    the JointScaler infrastructure simulation run metrics.
    """
    if not history_logs:
        print("Error: No simulation telemetry data found to visualize.")
        return

    # 1. Transform raw object logs into a structured Pandas DataFrame
    data = []
    for tick, (telemetry, nodes) in enumerate(history_logs):
        data.append({
            "Tick": tick,
            "CPU": telemetry.cpu_utilization * 100, # Convert to percentage
            "RAM": telemetry.ram_utilization * 100, # Convert to percentage
            "IOPS": telemetry.disk_io_ops,
            "Latency": telemetry.network_latency,
            "Nodes": nodes
        })
    df = pd.DataFrame(data)

    # 2. Initialize a 3-Row Interactive Subplot Figure
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "<b>Multi-Indicator Telemetry</b> (CPU & RAM Saturation Profiles)",
            "<b>System Operations Performance</b> (Network Latency Boundary Target: 30ms)",
            "<b>Fleet Infrastructure Capacity Allocation</b> (Active Scaled Node Pool)"
        )
    )

    # Panel 1: Resource Telemetry (CPU & RAM)
    fig.add_trace(go.Scatter(x=df["Tick"], y=df["CPU"], name="CPU Utilization (%)", mode='lines+markers', line=dict(color='#10b981', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Tick"], y=df["RAM"], name="RAM Utilization (%)", mode='lines', line=dict(color='#3b82f6', dash='dot')), row=1, col=1)

    # Panel 2: Latency Bottleneck Profile
    fig.add_trace(go.Scatter(x=df["Tick"], y=df["Latency"], name="Network Latency (ms)", mode='lines+markers', line=dict(color='#ef4444', width=2.5)), row=2, col=1)
    # Add a visual operational SLA limit marker line at 30ms
    fig.add_shape(type="line", x0=0, y0=30, x1=df["Tick"].max(), y1=30, line=dict(color="orange", width=1.5, dash="dash"), row=2, col=1)

    # Panel 3: Scaling Elastic Steps Action Loop
    fig.add_trace(go.Scatter(x=df["Tick"], y=df["Nodes"], name="Active Nodes Capacity", mode='lines+markers', line=dict(color='#8b5cf6', width=2), line_shape='hv'), row=3, col=1)

    # 3. Apply Unified Styling & Theme Formatting
    fig.update_layout(
        title_text="<b>JointScaler (IJCAI 2026) Infrastructure Simulation Analytics</b>",
        title_font_size=20,
        height=850,
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Update axis labels
    fig.update_yaxes(title_text="Utilization (%)", row=1, col=1)
    fig.update_yaxes(title_text="Latency (ms)", row=2, col=1)
    fig.update_yaxes(title_text="Cluster Nodes Count", row=3, col=1)
    fig.update_xaxes(title_text="Simulation Tick Steps (Time Windows)", row=3, col=1)

    # Export out completely standalone browser asset file
    fig.write_html(output_filename)
    print(f"\n🎉 Success: Interactive engineering dashboard compiled to '{output_filename}'!")