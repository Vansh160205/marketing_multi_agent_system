# mcp/client.py
import aiohttp
import websockets
import json
from typing import Dict, Any, Optional
from communication.jsonrpc_handler import JSONRPCHandler
from config import settings

class MCPClient:
    """Client for communicating with MCP Server"""
    
    def __init__(self, use_websocket: bool = False):
        self.http_url = f"http://{settings.MCP_HOST}:{settings.MCP_PORT}/rpc"
        self.ws_url = f"ws://{settings.MCP_HOST}:{settings.MCP_PORT}/ws"
        self.use_websocket = use_websocket
        self.ws_connection: Optional[websockets.WebSocketClientProtocol] = None
    
    async def connect_ws(self):
        """Establish WebSocket connection"""
        if not self.ws_connection:
            self.ws_connection = await websockets.connect(self.ws_url)
    
    async def request(self, method: str, params: Dict) -> Dict[str, Any]:
        """Make JSON-RPC request"""
        request_data = JSONRPCHandler.create_request(method, params)
        
        if self.use_websocket:
            return await self._request_ws(request_data)
        else:
            return await self._request_http(request_data)
    
    async def _request_http(self, request_data: str) -> Dict:
        """Make HTTP request"""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.http_url, json=json.loads(request_data)) as response:
                result = await response.json()
                if 'error' in result:
                    raise Exception(f"RPC Error: {result['error']}")
                return result.get('result', {})
    
    async def _request_ws(self, request_data: str) -> Dict:
        """Make WebSocket request"""
        if not self.ws_connection:
            await self.connect_ws()
        
        await self.ws_connection.send(request_data)
        response_data = await self.ws_connection.recv()
        result = json.loads(response_data)
        
        if 'error' in result:
            raise Exception(f"RPC Error: {result['error']}")
        return result.get('result', {})
    
    async def close(self):
        """Close connections"""
        if self.ws_connection:
            await self.ws_connection.close()