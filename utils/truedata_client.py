import os
import json
import asyncio
import websockets
from datetime import datetime
import threading
import queue

class TrueDataClient:
    def __init__(self):
        self.username = os.environ.get('TRUEDATA_USERNAME')
        self.password = os.environ.get('TRUEDATA_PASSWORD')
        self.realtime_port = 8084
        self.websocket_port = 8086
        self.base_url = "push.truedata.in"
        self.ws = None
        self.is_connected = False
        self.price_cache = {}
        self.message_queue = queue.Queue()
        self._running = False
    
    def get_websocket_url(self):
        return f"wss://{self.base_url}:{self.websocket_port}?user={self.username}&password={self.password}"
    
    async def _connect(self):
        try:
            url = self.get_websocket_url()
            self.ws = await websockets.connect(url, ping_interval=30, ping_timeout=10)
            self.is_connected = True
            print(f"TrueData WebSocket connected at {datetime.now()}")
            return True
        except Exception as e:
            print(f"TrueData connection error: {e}")
            self.is_connected = False
            return False
    
    async def _subscribe(self, symbols: list):
        if not self.is_connected or not self.ws:
            return False
        
        try:
            subscribe_msg = {
                "method": "addsymbol",
                "symbols": symbols
            }
            await self.ws.send(json.dumps(subscribe_msg))
            return True
        except Exception as e:
            print(f"Subscribe error: {e}")
            return False
    
    async def _listen(self):
        try:
            while self._running and self.ws:
                message = await self.ws.recv()
                data = json.loads(message)
                self._process_message(data)
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            print("TrueData connection closed")
        except Exception as e:
            print(f"Listen error: {e}")
    
    def _process_message(self, data):
        try:
            if isinstance(data, dict):
                symbol = data.get('symbol')
                if symbol:
                    self.price_cache[symbol] = {
                        'ltp': data.get('ltp', data.get('close')),
                        'open': data.get('open'),
                        'high': data.get('high'),
                        'low': data.get('low'),
                        'close': data.get('close'),
                        'volume': data.get('volume'),
                        'timestamp': data.get('timestamp', datetime.now().isoformat())
                    }
                    self.message_queue.put(data)
        except Exception as e:
            print(f"Process message error: {e}")
    
    def get_live_price(self, symbol: str):
        nse_symbol = symbol.replace('.NS', '').replace('.BO', '')
        return self.price_cache.get(nse_symbol, {}).get('ltp')
    
    def get_cached_prices(self):
        return self.price_cache.copy()
    
    def start_streaming(self, symbols: list):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def stream():
                self._running = True
                if await self._connect():
                    clean_symbols = [s.replace('.NS', '').replace('.BO', '') for s in symbols]
                    await self._subscribe(clean_symbols)
                    await self._listen()
            
            loop.run_until_complete(stream())
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def stop_streaming(self):
        self._running = False
        if self.ws:
            asyncio.get_event_loop().run_until_complete(self.ws.close())
        self.is_connected = False
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, timeframe: str = "1D"):
        pass
    
    def is_market_open(self):
        now = datetime.now()
        if now.weekday() >= 5:
            return False
        
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close


class TrueDataPriceFetcher:
    def __init__(self):
        self.client = TrueDataClient()
        self._initialized = False
    
    def initialize(self, symbols: list):
        if not self._initialized and self.client.username and self.client.password:
            try:
                self.client.start_streaming(symbols)
                self._initialized = True
                return True
            except Exception as e:
                print(f"TrueData initialization failed: {e}")
                return False
        return self._initialized
    
    def get_price(self, symbol: str):
        return self.client.get_live_price(symbol)
    
    def get_all_prices(self):
        return self.client.get_cached_prices()
    
    def is_available(self):
        return bool(self.client.username and self.client.password)
    
    def is_connected(self):
        return self.client.is_connected
