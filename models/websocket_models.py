"""
WebSocket Models for Analytics Microservice V2

Defines message structures for WebSocket communication.
These models wrap the existing analytics models without modification.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal, List
from datetime import datetime
import uuid


class WebSocketMessage(BaseModel):
    """Base WebSocket message structure"""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4()}")
    correlation_id: Optional[str] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        data = self.dict()
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AnalyticsRequestMessage(WebSocketMessage):
    """Analytics generation request via WebSocket"""
    type: Literal["analytics_request"] = "analytics_request"
    request_id: Optional[str] = Field(default_factory=lambda: f"req_{uuid.uuid4()}")
    payload: Dict[str, Any]  # Maps directly to AnalyticsRequest from existing models
    
    class Config:
        schema_extra = {
            "example": {
                "message_id": "msg_123",
                "correlation_id": "req_456",
                "session_id": "session_789",
                "type": "analytics_request",
                "payload": {
                    "content": "Show quarterly revenue growth for 2024",
                    "title": "Q1-Q4 2024 Revenue",
                    "use_synthetic_data": True,
                    "enhance_labels": True
                }
            }
        }


class AnalyticsResponseMessage(WebSocketMessage):
    """Analytics generation response"""
    type: Literal["analytics_response"] = "analytics_response"
    request_id: Optional[str] = None
    payload: Dict[str, Any]  # Contains chart, data, metadata from existing response
    
    class Config:
        schema_extra = {
            "example": {
                "message_id": "msg_resp_123",
                "correlation_id": "req_456",
                "session_id": "session_789",
                "type": "analytics_response",
                "payload": {
                    "success": True,
                    "chart": "base64_encoded_image",
                    "data": {
                        "labels": ["Q1", "Q2", "Q3", "Q4"],
                        "values": [45000, 52000, 48000, 61000]
                    },
                    "metadata": {
                        "chart_type": "bar_chart_vertical",
                        "generation_time_ms": 1250
                    }
                }
            }
        }


class StatusMessage(WebSocketMessage):
    """Progress status updates during processing"""
    type: Literal["status"] = "status"
    subtype: Optional[str] = None  # processing, completed, etc.
    payload: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "type": "status",
                "subtype": "processing",
                "payload": {
                    "status": "processing",
                    "message": "Selecting optimal chart type...",
                    "progress": 0.25
                }
            }
        }


class ErrorMessage(WebSocketMessage):
    """Error responses"""
    type: Literal["error"] = "error"
    payload: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "type": "error",
                "payload": {
                    "code": "GENERATION_FAILED",
                    "message": "Failed to generate chart",
                    "details": {
                        "reason": "Invalid data format"
                    }
                }
            }
        }


class ControlMessage(WebSocketMessage):
    """Control messages for connection management"""
    type: Literal["control"] = "control"
    subtype: str  # connection_ack, ping, pong, etc.
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "type": "control",
                "subtype": "connection_ack",
                "payload": {
                    "status": "connected",
                    "version": "2.0.0",
                    "capabilities": ["analytics_generation", "23_chart_types"]
                }
            }
        }


class BatchAnalyticsRequest(BaseModel):
    """Batch request for multiple analytics generations"""
    requests: List[Dict[str, Any]]
    batch_id: str = Field(default_factory=lambda: f"batch_{uuid.uuid4()}")
    
    class Config:
        schema_extra = {
            "example": {
                "batch_id": "batch_123",
                "requests": [
                    {
                        "content": "Q1 revenue breakdown",
                        "chart_type": "pie_chart"
                    },
                    {
                        "content": "Q2 revenue breakdown",
                        "chart_type": "pie_chart"
                    }
                ]
            }
        }