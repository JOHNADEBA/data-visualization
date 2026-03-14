# Real-Time Data Visualization Backend

A FastAPI-based WebSocket server that streams real-time data to Vue.js frontend.

## Features
- WebSocket connections for real-time data
- Multiple data sources (weather, stocks, crypto, mock)
- Configurable intervals and data points
- Auto-generated API docs at `/docs`

## Local Development

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate