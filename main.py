#!/usr/bin/env python3
"""
Analytics Microservice V2 - WebSocket Entry Point

A WebSocket-based microservice for analytics generation.
REUSES 90%+ of existing analytics_utils_v2 code.
"""

import asyncio
import logging
import sys
import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Local imports
from config.settings import get_settings
from api.websocket_handler import WebSocketHandler
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Analytics Microservice V2",
    description="WebSocket-based analytics generation service with 23 chart types",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global WebSocket handler
ws_handler: Optional[WebSocketHandler] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ws_handler
    
    logger.info("=" * 60)
    logger.info("Starting Analytics Microservice V2...")
    logger.info("=" * 60)
    
    # Check environment variables and log status
    env_status = []
    
    # Check critical environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        env_status.append("⚠️  GOOGLE_API_KEY not configured - LLM features disabled")
    else:
        env_status.append("✅ GOOGLE_API_KEY configured")
    
    # Log environment status
    logger.info("ENVIRONMENT VARIABLE STATUS:")
    for status in env_status:
        logger.info(status)
    logger.info("=" * 60)
    
    # Initialize WebSocket handler
    ws_handler = WebSocketHandler(settings)
    await ws_handler.initialize()
    
    # Log capabilities
    logger.info("ANALYTICS CAPABILITIES:")
    logger.info("✅ 23 Chart Types Supported")
    logger.info("✅ Synthetic Data Generation")
    logger.info("✅ LLM Enhancement")
    logger.info("✅ Advanced Theming")
    logger.info("✅ Real-time WebSocket Communication")
    logger.info("=" * 60)
    
    logger.info("Analytics Microservice V2 started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global ws_handler
    
    logger.info("Shutting down Analytics Microservice V2...")
    
    if ws_handler:
        await ws_handler.shutdown()
    
    logger.info("Analytics Microservice V2 shut down successfully")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Analytics Microservice V2",
        "version": "2.0.0",
        "status": "running",
        "description": "WebSocket-based analytics generation with 23 chart types",
        "websocket_url": f"{settings.ws_url}",
        "capabilities": {
            "chart_types": 23,
            "synthetic_data": True,
            "llm_enhancement": True,
            "batch_processing": True,
            "theme_customization": True
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "analytics-microservice-v2",
        "version": "2.0.0",
        "components": {}
    }
    
    # Check WebSocket handler
    if ws_handler:
        health_status["components"]["websocket_handler"] = "ready"
        health_status["components"]["active_connections"] = ws_handler.active_connections_count()
        
        # Get agent stats
        stats = ws_handler.get_stats()
        health_status["components"]["total_requests"] = stats.get("total_requests", 0)
        health_status["components"]["total_errors"] = stats.get("total_errors", 0)
    else:
        health_status["components"]["websocket_handler"] = "not_initialized"
        health_status["status"] = "degraded"
    
    # Check LLM configuration
    if settings.google_api_key:
        health_status["components"]["llm"] = "configured"
    else:
        health_status["components"]["llm"] = "not_configured"
        health_status["status"] = "degraded"
    
    return JSONResponse(
        status_code=200 if health_status["status"] == "healthy" else 503,
        content=health_status
    )


@app.get("/stats")
async def get_statistics():
    """Get service statistics"""
    if not ws_handler:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return ws_handler.get_stats()


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Query(..., description="Unique session identifier"),
    user_id: str = Query("anonymous", description="User identifier")
):
    """
    WebSocket endpoint for analytics generation.
    
    Query Parameters:
    - session_id: Unique session identifier (required)
    - user_id: User identifier (optional, defaults to "anonymous")
    
    Message Format:
    {
        "message_id": "msg_123",
        "correlation_id": "req_456",
        "session_id": "session_789",
        "type": "analytics_request",
        "payload": {
            "content": "Chart description",
            "title": "Chart Title",
            "data": [...],
            "theme": {...},
            ...
        }
    }
    """
    if not ws_handler:
        await websocket.close(code=1011, reason="Service not initialized")
        return
    
    await ws_handler.handle_connection(websocket, session_id, user_id)


@app.get("/chart-types")
async def get_chart_types():
    """Get list of supported chart types"""
    return {
        "chart_types": [
            {
                "category": "Line and Trend",
                "types": [
                    {"id": "line_chart", "name": "Line Chart"},
                    {"id": "step_chart", "name": "Step Chart"},
                    {"id": "area_chart", "name": "Area Chart"},
                    {"id": "stacked_area_chart", "name": "Stacked Area Chart"}
                ]
            },
            {
                "category": "Bar Charts",
                "types": [
                    {"id": "bar_chart_vertical", "name": "Vertical Bar Chart"},
                    {"id": "bar_chart_horizontal", "name": "Horizontal Bar Chart"},
                    {"id": "grouped_bar", "name": "Grouped Bar Chart"},
                    {"id": "stacked_bar", "name": "Stacked Bar Chart"}
                ]
            },
            {
                "category": "Distribution",
                "types": [
                    {"id": "histogram", "name": "Histogram"},
                    {"id": "box_plot", "name": "Box Plot"},
                    {"id": "violin_plot", "name": "Violin Plot"}
                ]
            },
            {
                "category": "Correlation",
                "types": [
                    {"id": "scatter_plot", "name": "Scatter Plot"},
                    {"id": "bubble_chart", "name": "Bubble Chart"},
                    {"id": "hexbin", "name": "Hexbin Plot"}
                ]
            },
            {
                "category": "Composition",
                "types": [
                    {"id": "pie_chart", "name": "Pie Chart"},
                    {"id": "waterfall", "name": "Waterfall Chart"},
                    {"id": "funnel", "name": "Funnel Chart"}
                ]
            },
            {
                "category": "Comparison",
                "types": [
                    {"id": "radar_chart", "name": "Radar Chart"},
                    {"id": "heatmap", "name": "Heatmap"}
                ]
            },
            {
                "category": "Statistical",
                "types": [
                    {"id": "error_bar", "name": "Error Bar Chart"},
                    {"id": "control_chart", "name": "Control Chart"},
                    {"id": "pareto", "name": "Pareto Chart"}
                ]
            },
            {
                "category": "Project",
                "types": [
                    {"id": "gantt", "name": "Gantt Chart"}
                ]
            }
        ],
        "total": 23
    }


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analytics Microservice V2")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    # Override with environment variable if set
    port = int(os.getenv("PORT", args.port))
    host = args.host
    
    # Log startup configuration
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {settings.debug_mode}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=args.reload or settings.debug_mode
    )