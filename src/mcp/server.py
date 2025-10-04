# mcp/server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List
import asyncio
from communication.jsonrpc_handler import JSONRPCHandler
from database.connection import db_manager
from sqlalchemy import text
from src.config import settings
import uuid,json

app = FastAPI(title="MCP Server - Model Context Protocol")

# JSON-RPC Handler
rpc_handler = JSONRPCHandler()

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Register RPC Methods
async def get_lead_data(params: Dict) -> Dict:
    """Get lead information"""
    lead_id = params.get('lead_id')
    email = params.get('email')
    
    async with db_manager.get_db_session() as session:
        if lead_id:
            query = text("SELECT * FROM leads WHERE id = :id")
            result = await session.execute(query, {'id': lead_id})
        elif email:
            query = text("SELECT * FROM leads WHERE email = :email")
            result = await session.execute(query, {'email': email})
        else:
            return {"error": "lead_id or email required"}
        
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {"error": "Lead not found"}
   
# After
async def update_lead_status(params: Dict) -> Dict:
    """Update lead status"""
    lead_id = params.get('lead_id')
    status = params.get('status')
    category = params.get('category')
    
    async with db_manager.get_db_session() as session:
        query = text("""
            UPDATE leads 
            SET status = :status, category = :category, updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """)
        result = await session.execute(query, {
            'id': lead_id,
            'status': status,
            'category': category
        })
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {"error": "Lead not found"}
    

async def get_campaign_metrics(params: Dict) -> Dict:
    """Get campaign performance metrics"""
    campaign_id = params.get('campaign_id')
    
    async with db_manager.get_db_session() as session:
        query = text("SELECT * FROM campaigns WHERE id = :id")
        result =await session.execute(query, {'id': campaign_id})
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {"error": "Campaign not found"}

async def log_interaction(params: Dict) -> Dict:
    """Log agent interaction"""
    async with db_manager.get_db_session() as session:
        query = text("""
            INSERT INTO interactions 
            (lead_id, campaign_id, agent_id, interaction_type, content, outcome, metadata)
            VALUES (:lead_id, :campaign_id, :agent_id, :type, :content, :outcome, :metadata)
            RETURNING id
        """)
        result = await session.execute(query, {
            'lead_id': params.get('lead_id'),
            'campaign_id': params.get('campaign_id'),
            'agent_id': params.get('agent_id'),
            'type': params.get('interaction_type'),
            'content': params.get('content'),
            'outcome': params.get('outcome'),
            'metadata': json.dumps(params.get('metadata', {}))
        })
        row = result.fetchone()
        return {"interaction_id": row[0], "status": "logged"}

async def agent_handoff(params: Dict) -> Dict:
    """Handle agent handoff with context preservation"""
    return {
        "handoff_id": str(uuid.uuid4()),
        "from_agent": params.get('from_agent'),
        "to_agent": params.get('to_agent'),
        "context": params.get('context'),
        "status": "completed"
    }

# Register all methods
rpc_handler.register_method('get_lead_data', get_lead_data)
rpc_handler.register_method('update_lead_status', update_lead_status)
rpc_handler.register_method('get_campaign_metrics', get_campaign_metrics)
rpc_handler.register_method('log_interaction', log_interaction)
rpc_handler.register_method('agent_handoff', agent_handoff)


# HTTP Endpoint for JSON-RPC
@app.post("/rpc")
async def rpc_endpoint(request: dict):
    """HTTP transport for JSON-RPC"""
    import json
    response = await rpc_handler.handle_request(json.dumps(request))
    return JSONResponse(content=json.loads(response))

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket transport for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await rpc_handler.handle_request(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MCP Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.MCP_HOST, port=settings.MCP_PORT)