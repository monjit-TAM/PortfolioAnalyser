"""WebSocket router for real-time portfolio updates

Note on Scalability:
For production deployments with multiple workers:
- Current implementation uses in-memory connection management
- For horizontal scaling, integrate Redis pub/sub for cross-worker communication
- Consider using a message broker (Redis, RabbitMQ) for price update distribution
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from typing import Dict, List, Set, Optional
import asyncio
import json
from datetime import datetime
import jwt

from api.services.auth_service import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/ws", tags=["WebSocket"])


async def verify_websocket_token(token: Optional[str] = Query(None)) -> Optional[dict]:
    """Verify JWT token for WebSocket connections
    
    WebSocket authentication is passed as a query parameter:
    ws://host/api/v1/ws/portfolio/client123?token=<jwt_token>
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except jwt.PyJWTError:
        return None


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
    
    def subscribe(self, client_id: str, symbols: List[str]):
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(symbols)
    
    def unsubscribe(self, client_id: str, symbols: List[str]):
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(symbols)
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def send_price_update(self, symbol: str, price: float, change: float):
        message = {
            "type": "price_update",
            "data": {
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_pct": round((change / (price - change)) * 100, 2) if price != change else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for client_id, subscribed_symbols in self.subscriptions.items():
            if symbol in subscribed_symbols:
                await self.send_personal_message(message, client_id)


manager = ConnectionManager()


@router.websocket("/portfolio/{client_id}")
async def websocket_portfolio_updates(
    websocket: WebSocket, 
    client_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time portfolio updates
    
    **Authentication**: Pass JWT token as query parameter:
    `ws://host/api/v1/ws/portfolio/{client_id}?token=<jwt_token>`
    
    Connect and subscribe to receive live price updates for portfolio stocks.
    
    Message format (send):
    ```json
    {
        "action": "subscribe",
        "symbols": ["RELIANCE", "TCS", "INFY"]
    }
    ```
    
    Message format (receive):
    ```json
    {
        "type": "price_update",
        "data": {
            "symbol": "RELIANCE",
            "price": 2450.50,
            "change": 12.30,
            "change_pct": 0.50
        },
        "timestamp": "2024-01-28T10:30:00Z"
    }
    ```
    """
    user = await verify_websocket_token(token)
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    await manager.connect(websocket, client_id)
    
    try:
        await manager.send_personal_message({
            "type": "connected",
            "message": "WebSocket connection established",
            "client_id": client_id,
            "user_id": user.get("user_id"),
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    symbols = message.get("symbols", [])
                    manager.subscribe(client_id, symbols)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "symbols": symbols,
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                
                elif action == "unsubscribe":
                    symbols = message.get("symbols", [])
                    manager.unsubscribe(client_id, symbols)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "symbols": symbols,
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                
                elif action == "get_prices":
                    symbols = message.get("symbols", [])
                    from utils.data_fetcher import DataFetcher
                    data_fetcher = DataFetcher()
                    
                    prices = {}
                    for symbol in symbols:
                        price = data_fetcher.get_current_price(symbol)
                        if price:
                            prices[symbol] = price
                    
                    await manager.send_personal_message({
                        "type": "prices",
                        "data": prices,
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                
                elif action == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON message",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@router.get("/connections")
async def get_active_connections():
    """Get count of active WebSocket connections (admin only)"""
    return {
        "active_connections": len(manager.active_connections),
        "total_subscriptions": sum(len(s) for s in manager.subscriptions.values())
    }
