# communication/jsonrpc_handler.py
import json
import uuid
from typing import Dict, Any, Callable
from datetime import datetime,date


# ADD THIS NEW CLASS
class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class JSONRPCHandler:
    """JSON-RPC 2.0 Protocol Handler"""
    
    def __init__(self):
        self.methods: Dict[str, Callable] = {}
    
    def register_method(self, name: str, handler: Callable):
        """Register RPC method"""
        self.methods[name] = handler
    
    async def handle_request(self, request_data: str) -> str:
        """Handle incoming JSON-RPC request"""
        try:
            request = json.loads(request_data)
            
            # Validate JSON-RPC 2.0 format
            if request.get('jsonrpc') != '2.0':
                return self._create_error(-32600, "Invalid Request", None)
            
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')
            
            # Check if method exists
            if method not in self.methods:
                return self._create_error(-32601, f"Method not found: {method}", request_id)
            
            # Execute method
            result = await self.methods[method](params)
            
            return self._create_response(result, request_id)
            
        except json.JSONDecodeError:
            return self._create_error(-32700, "Parse error", None)
        except Exception as e:
            return self._create_error(-32603, f"Internal error: {str(e)}", request.get('id'))
    
    def _create_response(self, result: Any, request_id: str) -> str:
        """Create JSON-RPC 2.0 success response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }, cls=CustomJSONEncoder)
    
    def _create_error(self, code: int, message: str, request_id: str) -> str:
        """Create JSON-RPC 2.0 error response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }, cls=CustomJSONEncoder)
    
    @staticmethod
    def create_request(method: str, params: Dict, request_id: str = None) -> str:
        """Create JSON-RPC 2.0 request"""
        return json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id or str(uuid.uuid4())
        })