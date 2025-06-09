# dashboard.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import json
import numpy as np
import pandas as pd
from datetime import datetime
import time
import os

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
LOG_FILE = "predictions_log.json"

# Constants for CRB calculation
C = 299792458.0  # Speed of light in m/s
FREQS = np.array([5e9, 5.5e9, 6e9])  # Frequencies in Hz

def calculate_crb(noise_std=0.01):
    """Calculate Cramér-Rao Bound for given noise level."""
    try:
        fisher_info = np.sum((2 * np.pi * FREQS / C)**2 / (noise_std**2))
        return 1 / fisher_info
    except Exception as e:
        print(f"Error calculating CRB: {e}")
        return 0.0

def load_latest_data():
    """Load the latest prediction data from the blockchain log."""
    try:
        if not os.path.exists(LOG_FILE):
            return {"distance": 0, "timestamp": time.time(), "phases": [0, 0, 0]}
            
        with open(LOG_FILE) as f:
            chain = json.load(f)
        if len(chain) > 1:  # Skip genesis block
            data = chain[-1]["data"]
            # Ensure timestamp is a float
            if "timestamp" in data:
                data["timestamp"] = float(data["timestamp"])
            return data
    except Exception as e:
        print(f"Error loading latest data: {e}")
    return {"distance": 0, "timestamp": time.time(), "phases": [0, 0, 0]}

def load_historical_data(n_points=100):
    try:
        if not os.path.exists(LOG_FILE):
            return pd.DataFrame()
        with open(LOG_FILE) as f:
            chain = json.load(f)
        if len(chain) > 1:
            data = []
            for block in chain[-n_points:]:
                # Only use blocks where data is a dict (skip genesis and malformed blocks)
                if isinstance(block.get("data"), dict):
                    block_data = block["data"].copy()
                    if "timestamp" in block_data:
                        block_data["timestamp"] = float(block_data["timestamp"])
                    data.append(block_data)
            df = pd.DataFrame(data)
            if not df.empty and "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            return df
    except Exception as e:
        print(f"Error loading historical data: {e}")
    return pd.DataFrame()

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Radar Range Estimation Dashboard", className="text-center mb-4"),
            html.Div(id="system-status", className="alert alert-info"),
            # Add explanation section
            dbc.Card([
                dbc.CardHeader("System Overview & Solution Explanation"),
                dbc.CardBody([
                    html.P("This dashboard is part of a modular, production-grade radar phase-unwrapping and range prediction system. The system simulates multi-frequency radar phase measurements, applies robust weighted CRT unwrapping, and uses ensemble machine learning (Random Forest, Huber regression) for robust range estimation. Predictions are streamed via MQTT, logged in a blockchain-style ledger, and visualized here. Optional AWS IoT and S3 backup, Docker deployment, and CRB/Fisher information analysis are supported as plug-and-play modules. The dashboard shows real-time and historical predictions, phase measurements, and theoretical estimation bounds (CRB)."),
                    html.Ul([
                        html.Li("Realistic radar simulation with phase noise (simulate.py)"),
                        html.Li("Weighted CRT unwrapping for robust range estimation (unwrap.py)"),
                        html.Li("Ensemble ML prediction (RandomForest, Huber) (train.py)"),
                        html.Li("Streaming and logging via MQTT/AWS/blockchain (predict.py, blockchain_log.py)"),
                        html.Li("Live dashboard visualization (this app)"),
                        html.Li("Docker and cloud support (optional)")
                    ]),
                    html.P("For details, see the codebase and documentation. The system is designed for real-world deployability and modularity.")
                ])
            ], className="mb-4")
        ])
    ]),
    
    dbc.Row([
        # Real-time distance display
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Current Distance"),
                dbc.CardBody([
                    html.H2(id="current-distance", className="text-center"),
                    html.P(id="last-update", className="text-muted text-center")
                ])
            ], className="mb-4")
        ], width=4),
        
        # Phase measurements
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Phase Measurements"),
                dbc.CardBody([
                    html.Div(id="phase-values")
                ])
            ], className="mb-4")
        ], width=4),
        
        # CRB display
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Cramér-Rao Bound"),
                dbc.CardBody([
                    html.Div(id="crb-value")
                ])
            ], className="mb-4")
        ], width=4)
    ]),
    
    dbc.Row([
        # Distance history plot
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distance History"),
                dbc.CardBody([
                    dcc.Graph(id="distance-plot")
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Phase history plot
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Phase History"),
                dbc.CardBody([
                    dcc.Graph(id="phase-plot")
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    # Hidden div for storing data
    html.Div(id="data-store", style={"display": "none"}),
    
    # Interval component for updates
    dcc.Interval(
        id="interval-component",
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

# Callbacks
@app.callback(
    [Output("current-distance", "children"),
     Output("last-update", "children"),
     Output("phase-values", "children"),
     Output("crb-value", "children"),
     Output("data-store", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_metrics(n):
    try:
        data = load_latest_data()
        distance = float(data.get("distance", 0))
        timestamp = float(data.get("timestamp", time.time()))
        phases = data.get("phases", [0, 0, 0])
        
        # Format current distance
        distance_str = f"{distance:.2f} m"
        
        # Format last update time
        last_update = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Format phase values
        phase_values = html.Div([
            html.P(f"Phase {i+1}: {float(phase):.2f} rad") for i, phase in enumerate(phases)
        ])
        
        # Calculate and format CRB
        crb = calculate_crb()
        crb_str = f"{crb:.4f} m"
        
        # Store data for other callbacks
        data_store = json.dumps(data)
        
        return distance_str, last_update, phase_values, crb_str, data_store
    except Exception as e:
        print(f"Error in update_metrics: {e}")
        return "0.00 m", "No data", html.Div(), "0.0000 m", "{}"

@app.callback(
    Output("distance-plot", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_distance_plot(n):
    try:
        df = load_historical_data()
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["distance"].astype(float),
            mode="lines",
            name="Distance"
        ))
        
        fig.update_layout(
            title="Distance History",
            xaxis_title="Time",
            yaxis_title="Distance (m)",
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        print(f"Error in update_distance_plot: {e}")
        return go.Figure()

@app.callback(
    Output("phase-plot", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_phase_plot(n):
    try:
        df = load_historical_data()
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        for i in range(len(FREQS)):
            if "phases" in df.columns:
                phases = df["phases"].apply(lambda x: float(x[i]) if isinstance(x, list) and len(x) > i else 0)
                fig.add_trace(go.Scatter(
                    x=df["timestamp"],
                    y=phases,
                    mode="lines",
                    name=f"Phase {i+1}"
                ))
        
        fig.update_layout(
            title="Phase History",
            xaxis_title="Time",
            yaxis_title="Phase (rad)",
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        print(f"Error in update_phase_plot: {e}")
        return go.Figure()

@app.callback(
    Output("system-status", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_system_status(n):
    try:
        if not os.path.exists(LOG_FILE):
            return "System Status: Waiting for data..."
            
        with open(LOG_FILE) as f:
            chain = json.load(f)
        last_update = datetime.fromtimestamp(float(chain[-1]["timestamp"])).strftime("%H:%M:%S")
        return f"System Status: Active | Last Update: {last_update} | Total Predictions: {len(chain)-1}"
    except Exception as e:
        print(f"Error in update_system_status: {e}")
        return "System Status: Error loading data"

if __name__ == "__main__":
    app.run_server(host="localhost", port=5000, debug=True)
