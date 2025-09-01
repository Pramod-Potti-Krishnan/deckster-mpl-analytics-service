"""
Constants for Analytics Microservice V2
"""

# Error codes
ERROR_CODES = {
    "INVALID_REQUEST": "The request format is invalid",
    "INVALID_JSON": "The JSON payload is malformed",
    "GENERATION_FAILED": "Chart generation failed",
    "UNKNOWN_MESSAGE_TYPE": "Unknown message type received",
    "INTERNAL_ERROR": "An internal server error occurred",
    "RATE_LIMITED": "Rate limit exceeded",
    "TIMEOUT": "Request timed out",
    "INVALID_CHART_TYPE": "Invalid or unsupported chart type",
    "INVALID_DATA": "Invalid data format provided",
    "LLM_ERROR": "LLM service error"
}

# Status messages
STATUS_MESSAGES = {
    "connected": "WebSocket connection established",
    "processing": "Processing analytics request",
    "completed": "Analytics generation completed",
    "failed": "Analytics generation failed",
    "disconnected": "WebSocket connection closed"
}

# Chart categories for organization
CHART_CATEGORIES = {
    "trend": ["line_chart", "step_chart", "area_chart", "stacked_area_chart"],
    "comparison": ["bar_chart_vertical", "bar_chart_horizontal", "grouped_bar", "stacked_bar"],
    "distribution": ["histogram", "box_plot", "violin_plot"],
    "correlation": ["scatter_plot", "bubble_chart", "hexbin"],
    "composition": ["pie_chart", "waterfall", "funnel"],
    "multi_dimensional": ["radar_chart", "heatmap"],
    "statistical": ["error_bar", "control_chart", "pareto"],
    "project": ["gantt"]
}

# WebSocket message types
WS_MESSAGE_TYPES = [
    "analytics_request",
    "analytics_response",
    "status",
    "error",
    "control",
    "ping",
    "pong"
]

# Default configuration values
DEFAULTS = {
    "max_message_size": 10 * 1024 * 1024,  # 10MB
    "ping_interval": 30,  # seconds
    "connection_timeout": 300,  # seconds
    "max_retries": 3,
    "retry_delay": 1000  # milliseconds
}