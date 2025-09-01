# Analytics Agent V2 - WebSocket Microservice Conversion Plan

## Executive Summary

This document outlines a comprehensive plan to convert the Analytics Agent V2 into a WebSocket-based microservice, following the successful pattern established by `diagram_microservice_v2`. The plan emphasizes **maximum code reuse** (90%+) while adding only the necessary WebSocket communication layer.

## Table of Contents
- [Objectives](#objectives)
- [Architecture Overview](#architecture-overview)
- [Implementation Phases](#implementation-phases)
- [Code Reuse Strategy](#code-reuse-strategy)
- [WebSocket API Specification](#websocket-api-specification)
- [Deployment Plan](#deployment-plan)
- [Timeline and Milestones](#timeline-and-milestones)
- [Risk Mitigation](#risk-mitigation)

## Objectives

### Primary Goals
1. **Maximum Code Reuse**: Preserve 90%+ of existing analytics_utils_v2 code
2. **WebSocket Communication**: Enable real-time, bidirectional analytics generation
3. **Railway Deployment**: Production-ready deployment on Railway platform
4. **API Compatibility**: Maintain backward compatibility with existing systems

### Success Criteria
- ✅ All 23 chart types functional via WebSocket
- ✅ No modifications to core analytics logic
- ✅ Sub-3 second response time for standard charts
- ✅ Concurrent request handling (10+ simultaneous)
- ✅ Production deployment with 99.9% uptime

## Architecture Overview

### Current Architecture (Monolithic)
```
User Request → AnalyticsAgentV2 → Direct Response
```

### Target Architecture (Microservice)
```
WebSocket Client ↔ WebSocket Handler ↔ AnalyticsAgentV2 (Unchanged)
                         ↓
                   Message Router
                         ↓
                   Status Updates
```

### Key Architectural Decisions
1. **Wrapper Pattern**: WebSocket layer wraps existing functionality
2. **Message Translation**: Convert WebSocket messages to/from existing models
3. **Stateless Core**: Analytics logic remains stateless and reusable
4. **Event-Driven Updates**: Real-time progress notifications

## Implementation Phases

### Phase 1: Project Structure Setup (Day 1 Morning)

#### Directory Structure
```
src/agents/analytics_microservice_v2/
├── analytics_utils_v2/          # ← COPIED AS-IS (no changes)
│   ├── __init__.py
│   ├── models.py
│   ├── conductor.py
│   ├── data_manager.py
│   ├── python_chart_agent.py
│   ├── theme_engine.py
│   ├── rate_limiter.py
│   ├── mcp_executor.py
│   ├── local_executor.py
│   ├── file_utils.py
│   └── analytics_playbook.py
├── api/                         # ← NEW
│   ├── __init__.py
│   └── websocket_handler.py    # WebSocket message handling
├── models/                      # ← NEW
│   ├── __init__.py
│   └── websocket_models.py     # WebSocket-specific models
├── core/                        # ← NEW
│   ├── __init__.py
│   └── analytics_conductor.py  # WebSocket-to-Analytics bridge
├── utils/                       # ← NEW (minimal)
│   ├── __init__.py
│   └── logger.py               # Logging configuration
├── config.py                    # ← NEW
├── main.py                      # ← NEW
├── requirements.txt             # ← EXTENDED
├── Dockerfile                   # ← NEW
├── railway.toml                 # ← NEW
└── .env.example                 # ← NEW
```

#### Actions Required
```bash
# 1. Copy entire analytics_utils_v2 directory
cp -r analytics_utils_v2 analytics_microservice_v2/analytics_utils_v2

# 2. Create new directories
mkdir -p analytics_microservice_v2/{api,models,core,utils}

# 3. Initialize Python packages
touch analytics_microservice_v2/{api,models,core,utils}/__init__.py
```

### Phase 2: WebSocket Models (Day 1 Afternoon)

#### File: `models/websocket_models.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import uuid

class WebSocketMessage(BaseModel):
    """Base WebSocket message structure"""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4()}")
    correlation_id: Optional[str] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str
    
class AnalyticsRequestMessage(WebSocketMessage):
    """Analytics generation request via WebSocket"""
    type: Literal["analytics_request"] = "analytics_request"
    payload: Dict[str, Any]  # Maps to AnalyticsRequest
    
class AnalyticsResponseMessage(WebSocketMessage):
    """Analytics generation response"""
    type: Literal["analytics_response"] = "analytics_response"
    payload: Dict[str, Any]  # Contains chart, data, metadata
    
class StatusMessage(WebSocketMessage):
    """Progress status updates"""
    type: Literal["status"] = "status"
    payload: Dict[str, Any]  # status, message, progress
    
class ErrorMessage(WebSocketMessage):
    """Error responses"""
    type: Literal["error"] = "error"
    payload: Dict[str, Any]  # code, message, details
```

### Phase 3: WebSocket Handler Implementation (Day 1-2)

#### File: `api/websocket_handler.py`
```python
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional

from analytics_utils_v2.analytics_agent_v2 import AnalyticsAgentV2
from analytics_utils_v2.models import AnalyticsRequest
from models.websocket_models import *
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WebSocketHandler:
    """
    WebSocket handler that wraps AnalyticsAgentV2
    REUSES all existing analytics logic
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.connections: Dict[str, WebSocket] = {}
        self.agent = None  # Lazy initialization
        
    async def initialize(self):
        """Initialize the analytics agent"""
        # Create single shared agent instance
        self.agent = AnalyticsAgentV2(
            mcp_tool=None,  # Configure based on settings
            api_name=self.settings.llm_provider
        )
        logger.info("Analytics agent initialized")
        
    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str
    ):
        """Handle WebSocket connection lifecycle"""
        
        # Store connection
        self.connections[session_id] = websocket
        
        # Send connection acknowledgment
        await self._send_control_message(
            session_id,
            "connection_ack",
            {
                "status": "connected",
                "version": "2.0.0",
                "capabilities": [
                    "analytics_generation",
                    "23_chart_types",
                    "synthetic_data",
                    "llm_enhancement",
                    "batch_processing"
                ]
            }
        )
        
        try:
            while True:
                # Receive and process messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Route to appropriate handler
                if message["type"] == "analytics_request":
                    await self._handle_analytics_request(
                        session_id, 
                        message
                    )
                elif message["type"] == "ping":
                    await self._send_pong(session_id)
                    
        except WebSocketDisconnect:
            logger.info(f"Connection closed: {session_id}")
        finally:
            del self.connections[session_id]
            
    async def _handle_analytics_request(
        self, 
        session_id: str, 
        message: Dict
    ):
        """
        Process analytics request
        REUSES existing AnalyticsAgentV2.generate()
        """
        correlation_id = message.get("correlation_id")
        
        try:
            # Send processing status
            await self._send_status(
                session_id,
                correlation_id,
                "processing",
                "Analyzing request..."
            )
            
            # Convert WebSocket payload to AnalyticsRequest
            # NO CHANGES to existing model
            request = AnalyticsRequest(**message["payload"])
            
            # REUSE existing generation logic completely
            response = await self.agent.generate(request)
            
            # Convert response to WebSocket format
            await self._send_analytics_response(
                session_id,
                correlation_id,
                response.to_api_response()
            )
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            await self._send_error(
                session_id,
                correlation_id,
                "GENERATION_FAILED",
                str(e)
            )
```

### Phase 4: FastAPI Application Setup (Day 2)

#### File: `main.py`
```python
#!/usr/bin/env python3
"""
Analytics Microservice v2 - WebSocket Entry Point
REUSES 90%+ of existing analytics_utils_v2 code
"""

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from api.websocket_handler import WebSocketHandler
from utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

app = FastAPI(
    title="Analytics Microservice v2",
    description="WebSocket-based analytics generation service",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global handler instance
ws_handler: Optional[WebSocketHandler] = None

@app.on_event("startup")
async def startup_event():
    """Initialize analytics service"""
    global ws_handler
    
    logger.info("Starting Analytics Microservice v2...")
    
    # Initialize WebSocket handler with existing agent
    ws_handler = WebSocketHandler(settings)
    await ws_handler.initialize()
    
    logger.info("Analytics Microservice ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global ws_handler
    
    if ws_handler:
        await ws_handler.shutdown()
        
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: str = "anonymous"
):
    """WebSocket endpoint for analytics generation"""
    await websocket.accept()
    
    if ws_handler:
        await ws_handler.handle_connection(
            websocket, 
            session_id, 
            user_id
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics-microservice-v2",
        "version": "2.0.0",
        "active_connections": len(ws_handler.connections) if ws_handler else 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.port),
        reload=settings.debug_mode
    )
```

### Phase 5: Configuration (Day 2)

#### File: `config.py`
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """
    Configuration settings
    REUSES existing environment variables
    """
    
    # Service configuration
    service_name: str = "analytics-microservice-v2"
    port: int = 8000
    debug_mode: bool = False
    
    # WebSocket configuration
    ws_url: str = "/ws"
    ws_timeout: int = 300  # 5 minutes
    max_connections: int = 100
    
    # LLM configuration (REUSED from existing)
    llm_provider: str = "gemini"
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # CORS configuration
    cors_origins: str = "*"
    
    # Analytics configuration (UNCHANGED)
    enable_synthetic_data: bool = True
    enable_llm_enhancement: bool = True
    default_theme: str = "modern"
    
    # Rate limiting (REUSED)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    
    def get_cors_origins_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return self.cors_origins.split(",")
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
```

## Code Reuse Strategy

### Components Reused Without Modification (90%+)
| Component | Files | Reuse % | Notes |
|-----------|-------|---------|-------|
| Core Analytics | `analytics_agent_v2.py` | 100% | No changes needed |
| Models | `models.py` | 100% | Existing models preserved |
| Conductor | `conductor.py` | 100% | Chart selection unchanged |
| Data Manager | `data_manager.py` | 100% | Data logic preserved |
| Chart Agents | `python_chart_agent.py` | 100% | Generation unchanged |
| Theme Engine | `theme_engine.py` | 100% | Theming preserved |
| Rate Limiter | `rate_limiter.py` | 100% | Throttling unchanged |
| Playbook | `analytics_playbook.py` | 100% | Rules preserved |
| Utilities | `file_utils.py`, etc. | 100% | Helpers unchanged |

### New Components (10%)
| Component | Purpose | Lines of Code |
|-----------|---------|---------------|
| WebSocket Handler | Message routing | ~200 |
| WebSocket Models | Message types | ~100 |
| FastAPI App | Service entry | ~100 |
| Configuration | Settings | ~50 |
| **Total New Code** | | **~450 lines** |

### Integration Pattern
```python
# WebSocket handler simply wraps existing functionality
async def handle_request(websocket_message):
    # 1. Extract payload
    payload = websocket_message["payload"]
    
    # 2. Create existing request object
    request = AnalyticsRequest(**payload)  # EXISTING MODEL
    
    # 3. Call existing agent
    response = await agent.generate(request)  # EXISTING METHOD
    
    # 4. Return via WebSocket
    await send_response(response.to_api_response())  # EXISTING METHOD
```

## WebSocket API Specification

### Connection URL
```
wss://analytics-service.up.railway.app/ws?session_id={SESSION_ID}&user_id={USER_ID}
```

### Message Types

#### Request Message
```json
{
  "message_id": "msg_123",
  "correlation_id": "req_456",
  "session_id": "session_789",
  "timestamp": "2025-01-20T10:30:00Z",
  "type": "analytics_request",
  "payload": {
    "content": "Show quarterly revenue growth for 2024",
    "title": "Q1-Q4 2024 Revenue",
    "data": null,
    "use_synthetic_data": true,
    "theme": {
      "primary": "#3B82F6",
      "secondary": "#10B981",
      "tertiary": "#F59E0B"
    },
    "chart_preference": null,
    "enhance_labels": true
  }
}
```

#### Response Message
```json
{
  "message_id": "msg_resp_123",
  "correlation_id": "req_456",
  "session_id": "session_789",
  "timestamp": "2025-01-20T10:30:02Z",
  "type": "analytics_response",
  "payload": {
    "success": true,
    "chart": "data:image/png;base64,...",
    "data": {
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "values": [45000, 52000, 48000, 61000],
      "statistics": {...}
    },
    "metadata": {
      "chart_type": "bar_chart_vertical",
      "generation_method": "python_mcp",
      "data_source": "synthetic",
      "generation_time_ms": 1250
    }
  }
}
```

#### Status Updates
```json
{
  "type": "status",
  "payload": {
    "status": "processing",
    "message": "Selecting optimal chart type...",
    "progress": 0.25
  }
}
```

### Client Example (JavaScript)
```javascript
class AnalyticsClient {
  constructor() {
    this.ws = null;
    this.sessionId = this.generateUUID();
  }
  
  async connect() {
    const url = `wss://analytics-service.up.railway.app/ws?session_id=${this.sessionId}&user_id=web_client`;
    this.ws = new WebSocket(url);
    
    return new Promise((resolve) => {
      this.ws.onopen = () => resolve();
      this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    });
  }
  
  async generateChart(content, options = {}) {
    const request = {
      message_id: `msg_${this.generateUUID()}`,
      correlation_id: `req_${this.generateUUID()}`,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      type: "analytics_request",
      payload: {
        content,
        ...options
      }
    };
    
    this.ws.send(JSON.stringify(request));
    // Handle async response via onmessage
  }
}
```

## Deployment Plan

### Railway Deployment Configuration

#### File: `railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[env]
GOOGLE_API_KEY = "${{GOOGLE_API_KEY}}"
DEBUG_MODE = "false"
RATE_LIMIT_ENABLED = "true"
```

#### File: `Dockerfile` (Alternative)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application (including unchanged analytics_utils_v2)
COPY . .

# Expose port
EXPOSE 8000

# Start service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
DEBUG_MODE=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
CORS_ORIGINS=*
```

### Deployment Steps
1. **Create Railway Project**
   ```bash
   railway login
   railway init
   ```

2. **Configure Environment**
   ```bash
   railway variables set GOOGLE_API_KEY=your_key
   ```

3. **Deploy Service**
   ```bash
   railway up
   ```

4. **Verify Deployment**
   - Check health: `https://your-service.up.railway.app/health`
   - Test WebSocket: Use provided client examples

## Timeline and Milestones

### Day 1: Foundation (8 hours)
- [x] Morning: Project structure setup
- [x] Afternoon: WebSocket models and configuration
- [x] Evening: Initial WebSocket handler

### Day 2: Integration (8 hours)
- [ ] Morning: Complete WebSocket handler
- [ ] Afternoon: FastAPI application setup
- [ ] Evening: Local testing and debugging

### Day 3: Deployment (4 hours)
- [ ] Morning: Railway deployment setup
- [ ] Afternoon: Production testing and monitoring

### Total Estimated Time: 20 hours (2.5 days)

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| WebSocket connection drops | Medium | Low | Implement auto-reconnect |
| Memory leaks from connections | Low | High | Connection cleanup handlers |
| Rate limiting issues | Medium | Medium | Reuse existing limiter |
| Chart generation timeouts | Low | Medium | Async processing with status |

### Mitigation Strategies
1. **Connection Management**: Implement heartbeat/ping-pong
2. **Resource Cleanup**: Proper connection lifecycle management
3. **Error Recovery**: Graceful degradation and retries
4. **Monitoring**: Health checks and metrics endpoints

## Testing Strategy

### Unit Tests (Existing - No Changes)
```python
# All existing tests remain valid
pytest analytics_utils_v2/tests/
```

### Integration Tests (New)
```python
# Test WebSocket communication
async def test_websocket_connection():
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(test_request))
        response = await ws.recv()
        assert json.loads(response)["type"] == "analytics_response"
```

### Load Testing
```bash
# Artillery configuration for WebSocket load testing
artillery run websocket-load-test.yml
```

## Monitoring and Observability

### Health Metrics
- Active WebSocket connections
- Request processing time
- Chart generation success rate
- LLM API usage

### Logging Strategy
```python
# Structured logging for production
logger.info("analytics_generated", extra={
    "session_id": session_id,
    "chart_type": chart_type,
    "generation_time_ms": time_ms,
    "success": True
})
```

## Migration Strategy

### Phase 1: Parallel Operation
- Deploy WebSocket service alongside existing system
- Route new clients to WebSocket
- Maintain existing API for legacy clients

### Phase 2: Gradual Migration
- Update clients to use WebSocket
- Monitor performance and stability
- Maintain fallback to HTTP if needed

### Phase 3: Deprecation
- Announce deprecation timeline
- Final migration of remaining clients
- Decommission old endpoints

## Success Metrics

### Performance KPIs
- **Response Time**: < 3 seconds for 95% of requests
- **Throughput**: 100+ charts per minute
- **Availability**: 99.9% uptime
- **Error Rate**: < 1% failed generations

### Business Metrics
- **Adoption Rate**: 80% clients using WebSocket within 1 month
- **User Satisfaction**: Improved real-time feedback
- **Resource Efficiency**: 30% reduction in server load
- **Development Velocity**: 50% faster feature deployment

## Conclusion

This conversion plan provides a clear path to transform Analytics Agent V2 into a production-ready WebSocket microservice while **preserving 90%+ of existing code**. The wrapper-based approach ensures:

1. **Minimal Risk**: Core logic remains untouched
2. **Fast Implementation**: 2-3 days total effort
3. **Easy Maintenance**: Clear separation of concerns
4. **Future Flexibility**: Easy to add features

The plan follows proven patterns from `diagram_microservice_v2` while adapting to the specific needs of analytics generation. With careful execution, this conversion will deliver a robust, scalable microservice that enhances the user experience through real-time communication.

---

*Document Version: 1.0*
*Created: January 2025*
*Status: Ready for Implementation*