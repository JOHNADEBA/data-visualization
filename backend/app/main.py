from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
import httpx
from datetime import datetime
from typing import Dict, Set
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Get environment
is_production = os.getenv("RENDER", False) or os.getenv("PRODUCTION", False)

# Configure CORS based on environment
if is_production:
    # In production, only allow your Vue app
    frontend_url = os.getenv("FRONTEND_URL", "https://your-vue-app.com")
    allow_origins = [frontend_url]
else:
    # In development, allow localhost
    allow_origins = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Vue CLI
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Real-time Data Viz API",
        "status": "running",
        "environment": "production" if is_production else "development",
        "features": {
            "weather": bool(os.getenv("OPENWEATHER_API_KEY")),
            "crypto": True  # CoinGecko doesn't need a key
        },
        "websocket_endpoint": "/ws/{client_id}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_streams: Dict[str, dict] = {}  # Store stream params
        self.stream_tasks: Dict[str, asyncio.Task] = {}  # Store running tasks

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        await self.send_message(client_id, {
            "type": "system",
            "message": f"Connected successfully! Your client ID: {client_id}",
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # Cancel streaming task if exists
            if client_id in self.stream_tasks:
                self.stream_tasks[client_id].cancel()
                del self.stream_tasks[client_id]
            if client_id in self.active_streams:
                del self.active_streams[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
                return True
            except:
                self.disconnect(client_id)
                return False
        return False

    def update_stream_params(self, client_id: str, params: dict):
        if client_id in self.active_streams:
            self.active_streams[client_id].update(params)
            return True
        return False

    def get_stream_params(self, client_id: str) -> dict:
        return self.active_streams.get(client_id, {})

    def set_stream_task(self, client_id: str, task: asyncio.Task):
        self.stream_tasks[client_id] = task

    def is_streaming(self, client_id: str) -> bool:
        return client_id in self.active_streams

# Create global connection manager
manager = ConnectionManager()

# ============ REAL API FETCHERS ============

async def fetch_real_weather(city: str) -> dict:
    """Fetch real weather data from OpenWeatherMap"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # If no API key, return mock data with realistic temperatures
    if not api_key or api_key == "your_api_key_here":
        return {
            "source": "weather",
            "value": round(random.uniform(5, 35), 1),
            "unit": "celsius",
            "location": city,
            "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"]),
            "humidity": random.randint(40, 90),
            "feels_like": round(random.uniform(5, 35), 1),
            "pressure": random.randint(980, 1030),
            "is_mock": True
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": api_key,
                    "units": "metric"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "weather",
                    "value": round(data["main"]["temp"], 1),
                    "unit": "celsius",
                    "location": city,
                    "conditions": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "pressure": data["main"]["pressure"],
                    "timestamp": datetime.now().isoformat(),
                    "is_mock": False
                }
    except Exception:
        pass  # Silently fall back to mock data
    
    # Fallback to mock data
    return {
        "source": "weather",
        "value": round(random.uniform(5, 35), 1),
        "unit": "celsius",
        "location": city,
        "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"]),
        "humidity": random.randint(40, 90),
        "feels_like": round(random.uniform(5, 35), 1),
        "pressure": random.randint(980, 1030),
        "is_mock": True
    }

async def fetch_real_crypto(coin: str) -> dict:
    """Fetch real crypto data from CoinGecko (no API key needed)"""
    coin_map = {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "cardano": "cardano",
        "dogecoin": "dogecoin",
        "ripple": "ripple",
        "solana": "solana"
    }
    
    coin_id = coin_map.get(coin.lower(), coin.lower())
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_last_updated_at": "true"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        "source": "crypto",
                        "value": coin_data["usd"],
                        "unit": "USD",
                        "coin": coin,
                        "change": round(coin_data.get("usd_24h_change", 0), 2),
                        "volume": round(coin_data.get("usd_24h_vol", 0), 0),
                        "timestamp": datetime.now().isoformat(),
                        "is_mock": False
                    }
    except Exception:
        pass  # Silently fall back to mock data
    
    # Fallback to mock data
    return {
        "source": "crypto",
        "value": round(random.uniform(20000, 60000), 0),
        "unit": "USD",
        "coin": coin,
        "change": round(random.uniform(-5, 5), 2),
        "volume": round(random.uniform(1000, 10000), 0),
        "is_mock": True
    }

async def fetch_mock_data(source: str, params: dict) -> dict:
    """Mock data for stock and other sources"""
    
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    if source == "stock":
        return {
            "source": "stock",
            "value": round(random.uniform(100, 500), 2),
            "unit": "USD",
            "symbol": params.get("symbol", "AAPL"),
            "change": round(random.uniform(-5, 5), 2),
            "volume": random.randint(100000, 10000000),
            "is_mock": True
        }
    else:  # mock/default
        return {
            "source": "mock",
            "value": round(random.uniform(0, 100), 1),
            "unit": "arbitrary",
            "is_mock": True
        }

async def stream_data(client_id: str):
    """Stream data continuously to the client until stopped"""
    
    try:
        point_number = 1
        while client_id in manager.active_streams:
            # Get current parameters (may have been updated)
            params = manager.active_streams[client_id]
            
            sources = params.get("sources", ["mock"])
            interval = max(0.5, float(params.get("interval", 2)))
            
            # Collect data from all sources
            for source in sources:
                if source == "weather":
                    city = params.get("city", "London")
                    data_point = await fetch_real_weather(city)
                elif source == "crypto":
                    coin = params.get("coin", "bitcoin")
                    data_point = await fetch_real_crypto(coin)
                else:
                    data_point = await fetch_mock_data(source, params)
                
                # Send to client
                await manager.send_message(client_id, {
                    "type": "data",
                    "point_number": point_number,
                    "timestamp": datetime.now().isoformat(),
                    "data": data_point
                })
                
                # Small delay between sources
                if len(sources) > 1:
                    await asyncio.sleep(0.2)
            
            # Send batch completion status
            await manager.send_message(client_id, {
                "type": "status",
                "point_number": point_number,
                "message": f"Received batch {point_number}",
                "timestamp": datetime.now().isoformat()
            })
            
            point_number += 1
            
            # Wait for next interval
            await asyncio.sleep(interval)
        
    except asyncio.CancelledError:
        pass  # Stream was cancelled intentionally
    except Exception:
        # Send error message to client
        await manager.send_message(client_id, {
            "type": "error",
            "message": "Stream error occurred",
            "timestamp": datetime.now().isoformat()
        })
    finally:
        # Clean up
        if client_id in manager.stream_tasks:
            del manager.stream_tasks[client_id]
        if client_id in manager.active_streams:
            del manager.active_streams[client_id]

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Check if this is an update message
                if message.get("type") == "UPDATE_STREAM":
                    # Update existing stream parameters
                    if "sources" in message:
                        manager.active_streams[client_id]["sources"] = message["sources"]
                        await manager.send_message(client_id, {
                            "type": "system",
                            "message": f"Updated sources: {message['sources']}",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    if "interval" in message:
                        manager.active_streams[client_id]["interval"] = message["interval"]
                    
                    if "city" in message:
                        manager.active_streams[client_id]["city"] = message["city"]
                    
                    if "symbol" in message:
                        manager.active_streams[client_id]["symbol"] = message["symbol"]
                    
                    if "coin" in message:
                        manager.active_streams[client_id]["coin"] = message["coin"]
                    
                    continue
                
                # Regular start stream message
                if manager.is_streaming(client_id):
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Already streaming. Send UPDATE_STREAM to modify.",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Validate parameters
                if not message.get("sources"):
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Please specify at least one data source",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Store stream parameters
                manager.active_streams[client_id] = message
                
                # Acknowledge receipt and start streaming
                await manager.send_message(client_id, {
                    "type": "stream_started",
                    "message": "Starting continuous data stream",
                    "params": {
                        "sources": message.get("sources"),
                        "interval": message.get("interval", 2),
                    },
                    "timestamp": datetime.now().isoformat()
                })
                
                # Start streaming in the background
                task = asyncio.create_task(stream_data(client_id))
                manager.set_stream_task(client_id, task)
                
            except json.JSONDecodeError:
                await manager.send_message(client_id, {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception:
        manager.disconnect(client_id)

# Keep-alive endpoint for uptime monitoring
@app.get("/ping")
async def ping():
    return {"pong": datetime.now().isoformat()}