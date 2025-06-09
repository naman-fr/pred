# Radar Phase-Unwrapping Spacing Prediction System

This project implements a real-time radar phase-unwrapping spacing prediction system using MQTT for communication and a web-based dashboard for visualization.

## Features

- Real-time phase data processing and distance prediction
- MQTT-based communication system
- Interactive web dashboard for data visualization
- Historical data tracking and analysis
- Machine learning-based prediction models

## System Architecture

The system consists of several components:

1. **MQTT Broker**: Handles real-time communication between components
2. **Publisher**: Simulates radar phase data
3. **Predictor**: Processes phase data and predicts distances
4. **Dashboard**: Web interface for data visualization
5. **Blockchain Logger**: Records predictions for audit trail

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the MQTT broker:
```bash
python simple_broker.py
```

3. Run the predictor:
```bash
python predict.py
```

4. Start the dashboard:
```bash
python dashboard.py
```

5. (Optional) Run the publisher for testing:
```bash
python publisher.py
```

## Configuration

- MQTT broker runs on `localhost:1883`
- Dashboard is accessible at `http://localhost:5000`
- Default MQTT topic for phase data: `radar/phases`

## Dependencies

See `requirements.txt` for a complete list of dependencies.

## License

MIT License 