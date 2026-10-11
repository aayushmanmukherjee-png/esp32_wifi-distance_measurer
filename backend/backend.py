import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import json

app = FastAPI(title="ESP32 Distance Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration (Retrieved from environment variables for Render deployment)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ihrmxsdrwbqavxpvjyvt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_YqaaEZcNHa4hjQwvtYne9Q_K0rikiz_")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class RegulatorSettings(BaseModel):
    threshold: float
    mode: str
    regulator: bool

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.post("/api/log-distance")
async def log_distance(data: dict):
    try:
        distance = data.get("distance")
        # Insert telemetry record into Supabase table 'distance_logs'
        response = supabase.table("distance_logs").insert({"distance": distance}).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    try:
        response = supabase.table("distance_logs").select("*").order("created_at", desc=True).limit(50).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast telemetry or control commands to all connected UI clients
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)