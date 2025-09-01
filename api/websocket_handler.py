"""
WebSocket Handler for Analytics Generation

This handler wraps the existing AnalyticsAgentV2 without any modifications.
All analytics logic is preserved and reused completely.
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import traceback
from fastapi import WebSocket, WebSocketDisconnect


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Import existing analytics components - NO MODIFICATIONS
from analytics_agent_v2 import AnalyticsAgentV2, create_analytics_v2
from analytics_utils_v2.models import AnalyticsRequest, ThemeConfig, ChartType

# Import WebSocket models
from models.websocket_models import (
    AnalyticsRequestMessage,
    AnalyticsResponseMessage,
    StatusMessage,
    ErrorMessage,
    ControlMessage
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket, metadata: Dict[str, Any]):
        """Add new connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = metadata
        logger.info(f"Connection established: {session_id} (user: {metadata.get('user_id')})")
    
    async def disconnect(self, session_id: str):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            metadata = self.connection_metadata.pop(session_id, {})
            logger.info(f"Connection closed: {session_id} (user: {metadata.get('user_id')})")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            # Use custom encoder to handle datetime objects
            json_str = json.dumps(message, cls=DateTimeEncoder)
            await websocket.send_text(json_str)
    
    def get_connection_count(self) -> int:
        """Get active connection count"""
        return len(self.active_connections)


class WebSocketHandler:
    """
    WebSocket handler that wraps AnalyticsAgentV2.
    REUSES all existing analytics logic without modification.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.connection_manager = ConnectionManager()
        self.agent: Optional[AnalyticsAgentV2] = None
        self.total_requests = 0
        self.total_errors = 0
        self.active_requests: Dict[str, asyncio.Task] = {}
    
    async def initialize(self):
        """Initialize the analytics agent"""
        logger.info("Initializing WebSocket handler for Analytics...")
        
        # Create single shared agent instance - REUSING existing agent
        self.agent = AnalyticsAgentV2(
            mcp_tool=None,  # Configure based on settings if needed
            api_name=self.settings.llm_provider
        )
        
        logger.info("Analytics WebSocket handler initialized successfully")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info("Shutting down Analytics WebSocket handler...")
        
        # Cancel active requests
        for task in self.active_requests.values():
            task.cancel()
        
        # Close all connections
        for session_id in list(self.connection_manager.active_connections.keys()):
            await self.connection_manager.disconnect(session_id)
        
        logger.info("Analytics WebSocket handler shut down")
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str = "anonymous"
    ):
        """Handle WebSocket connection lifecycle"""
        
        # Store connection
        await self.connection_manager.connect(
            session_id,
            websocket,
            {
                "user_id": user_id,
                "connected_at": datetime.utcnow(),
                "request_count": 0
            }
        )
        
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
                    "batch_processing",
                    "theme_customization"
                ],
                "protocol": "analytics_v2"
            }
        )
        
        try:
            # Message loop
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                # Parse and handle message
                try:
                    message_data = json.loads(data)
                    await self._handle_message(session_id, message_data)
                    
                except json.JSONDecodeError as e:
                    await self._send_error(
                        session_id,
                        None,
                        "INVALID_JSON",
                        f"Invalid JSON: {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Message handling error: {e}", exc_info=True)
                    await self._send_error(
                        session_id,
                        None,
                        "INTERNAL_ERROR",
                        "An internal error occurred"
                    )
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}", exc_info=True)
        finally:
            await self.connection_manager.disconnect(session_id)
            # Clean up any active requests for this session
            for request_id in list(self.active_requests.keys()):
                if request_id.startswith(session_id):
                    task = self.active_requests.pop(request_id)
                    task.cancel()
    
    async def _handle_message(self, session_id: str, message: Dict[str, Any]):
        """Route message to appropriate handler"""
        message_type = message.get("type")
        
        if message_type == "analytics_request":
            # Handle analytics generation request
            task = asyncio.create_task(
                self._handle_analytics_request(session_id, message)
            )
            request_id = message.get("correlation_id", message.get("message_id"))
            self.active_requests[f"{session_id}_{request_id}"] = task
            
        elif message_type == "ping":
            # Handle ping
            await self._send_control_message(session_id, "pong", {})
            
        elif message_type == "control":
            # Handle control messages
            subtype = message.get("subtype")
            if subtype == "ping":
                await self._send_control_message(session_id, "pong", {})
                
        else:
            await self._send_error(
                session_id,
                message.get("correlation_id"),
                "UNKNOWN_MESSAGE_TYPE",
                f"Unknown message type: {message_type}"
            )
    
    async def _handle_analytics_request(self, session_id: str, message: Dict[str, Any]):
        """
        Process analytics request.
        REUSES existing AnalyticsAgentV2.generate() completely.
        """
        correlation_id = message.get("correlation_id", message.get("message_id"))
        request_id = message.get("request_id", correlation_id)
        
        try:
            self.total_requests += 1
            
            # Update connection metadata
            if session_id in self.connection_manager.connection_metadata:
                self.connection_manager.connection_metadata[session_id]["request_count"] += 1
            
            # Send initial status
            await self._send_status(
                session_id,
                correlation_id,
                "processing",
                "Initializing analytics generation...",
                0.1
            )
            
            # Extract payload
            payload = message.get("payload", {})
            
            # Convert theme if provided
            theme = None
            if "theme" in payload and payload["theme"]:
                theme = ThemeConfig(**payload["theme"])
                payload["theme"] = theme
            
            # Convert chart preference if provided
            if "chart_preference" in payload and payload["chart_preference"]:
                try:
                    payload["chart_preference"] = ChartType(payload["chart_preference"])
                except ValueError:
                    # Invalid chart type, let the agent handle it
                    pass
            
            # Send status update
            await self._send_status(
                session_id,
                correlation_id,
                "processing",
                "Analyzing request and selecting chart type...",
                0.25
            )
            
            # Create AnalyticsRequest from payload - REUSING existing model
            request = AnalyticsRequest(**payload)
            
            # Send status update
            await self._send_status(
                session_id,
                correlation_id,
                "processing",
                "Generating chart...",
                0.5
            )
            
            # Call existing agent - COMPLETELY REUSING existing generation logic
            response = await self.agent.generate(request)
            
            # Send status update
            await self._send_status(
                session_id,
                correlation_id,
                "processing",
                "Finalizing response...",
                0.9
            )
            
            # Convert response to API format - REUSING existing method
            api_response = response.to_api_response()
            
            # Send analytics response
            await self._send_analytics_response(
                session_id,
                correlation_id,
                request_id,
                api_response
            )
            
            logger.info(f"Analytics generated successfully for {session_id} ({correlation_id})")
            
        except Exception as e:
            self.total_errors += 1
            logger.error(f"Analytics generation failed: {e}", exc_info=True)
            await self._send_error(
                session_id,
                correlation_id,
                "GENERATION_FAILED",
                str(e),
                {"traceback": traceback.format_exc()}
            )
        finally:
            # Remove from active requests
            self.active_requests.pop(f"{session_id}_{request_id}", None)
    
    async def _send_analytics_response(
        self,
        session_id: str,
        correlation_id: str,
        request_id: str,
        response: Dict[str, Any]
    ):
        """Send analytics response message"""
        message = AnalyticsResponseMessage(
            correlation_id=correlation_id,
            request_id=request_id,
            session_id=session_id,
            payload=response
        )
        await self.connection_manager.send_message(session_id, message.to_json())
    
    async def _send_status(
        self,
        session_id: str,
        correlation_id: Optional[str],
        status: str,
        message: str,
        progress: float = 0.0
    ):
        """Send status update message"""
        status_msg = StatusMessage(
            correlation_id=correlation_id,
            session_id=session_id,
            subtype=status,
            payload={
                "status": status,
                "message": message,
                "progress": progress
            }
        )
        await self.connection_manager.send_message(session_id, status_msg.to_json())
    
    async def _send_error(
        self,
        session_id: str,
        correlation_id: Optional[str],
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send error message"""
        error_msg = ErrorMessage(
            correlation_id=correlation_id,
            session_id=session_id,
            payload={
                "code": code,
                "message": message,
                "details": details or {}
            }
        )
        await self.connection_manager.send_message(session_id, error_msg.to_json())
    
    async def _send_control_message(
        self,
        session_id: str,
        subtype: str,
        payload: Dict[str, Any]
    ):
        """Send control message"""
        control_msg = ControlMessage(
            session_id=session_id,
            subtype=subtype,
            payload=payload
        )
        await self.connection_manager.send_message(session_id, control_msg.to_json())
    
    def active_connections_count(self) -> int:
        """Get active connections count"""
        return self.connection_manager.get_connection_count()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return {
            "active_connections": self.active_connections_count(),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "active_requests": len(self.active_requests),
            "agent_stats": self.agent.get_stats() if self.agent else {}
        }