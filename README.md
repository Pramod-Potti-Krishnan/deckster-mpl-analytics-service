# Analytics Microservice V2

A production-ready WebSocket-based microservice for AI-powered analytics generation with 23 chart types.

## Features

- ✅ **23 Chart Types**: Complete coverage from basic bar charts to complex statistical visualizations
- ✅ **WebSocket Communication**: Real-time, bidirectional analytics generation
- ✅ **AI-Powered**: Intelligent chart selection and data generation using LLMs
- ✅ **Synthetic Data**: Automatic data generation when user data not provided
- ✅ **Advanced Theming**: Customizable color schemes with gradient support
- ✅ **90%+ Code Reuse**: Built on proven analytics_utils_v2 foundation
- ✅ **Production Ready**: Docker and Railway deployment configurations included

## Quick Start

### Local Development

1. **Clone and navigate to the directory:**
```bash
cd src/agents/analytics_microservice_v2
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

5. **Run the service:**
```bash
python main.py
```

The service will be available at:
- WebSocket: `ws://localhost:8000/ws`
- HTTP API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`

## WebSocket API

### Connection

Connect to the WebSocket endpoint with required query parameters:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?session_id=uuid-here&user_id=user123');
```

### Request Format

```json
{
  "message_id": "msg_123",
  "correlation_id": "req_456",
  "session_id": "session_789",
  "type": "analytics_request",
  "payload": {
    "content": "Show quarterly revenue growth for 2024",
    "title": "Q1-Q4 2024 Revenue",
    "use_synthetic_data": true,
    "enhance_labels": true,
    "theme": {
      "primary": "#3B82F6",
      "secondary": "#10B981"
    }
  }
}
```

### Response Format

```json
{
  "type": "analytics_response",
  "correlation_id": "req_456",
  "payload": {
    "success": true,
    "chart": "base64_encoded_png",
    "data": {
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "values": [45000, 52000, 48000, 61000],
      "statistics": {...}
    },
    "metadata": {
      "chart_type": "bar_chart_vertical",
      "generation_time_ms": 1250
    }
  }
}
```

## Supported Chart Types

### Line and Trend
- `line_chart` - Time series and trends
- `step_chart` - Discrete changes
- `area_chart` - Volume over time
- `stacked_area_chart` - Part-to-whole trends

### Bar Charts
- `bar_chart_vertical` - Category comparison
- `bar_chart_horizontal` - Long labels
- `grouped_bar` - Multi-series comparison
- `stacked_bar` - Part-to-whole

### Distribution
- `histogram` - Frequency distribution
- `box_plot` - Statistical summary
- `violin_plot` - Distribution shape

### Correlation
- `scatter_plot` - Correlation analysis
- `bubble_chart` - 3D relationships
- `hexbin` - Dense scatter data

### Composition
- `pie_chart` - Part-to-whole
- `waterfall` - Incremental changes
- `funnel` - Process stages

### Comparison
- `radar_chart` - Multi-dimensional
- `heatmap` - Matrix relationships

### Statistical
- `error_bar` - Uncertainty ranges
- `control_chart` - Process monitoring
- `pareto` - 80/20 analysis

### Project
- `gantt` - Project timeline

## Deployment

### Docker

```bash
# Build image
docker build -t analytics-microservice-v2 .

# Run container
docker run -p 8000:8000 --env-file .env analytics-microservice-v2
```

### Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Set environment variables:
```bash
railway variables set GOOGLE_API_KEY=your_key_here
```

4. Deploy:
```bash
railway up
```

## Client Examples

### JavaScript/Browser

```javascript
class AnalyticsClient {
  constructor() {
    this.ws = null;
    this.sessionId = this.generateUUID();
  }
  
  async connect() {
    const url = `ws://localhost:8000/ws?session_id=${this.sessionId}&user_id=web_client`;
    this.ws = new WebSocket(url);
    
    return new Promise((resolve) => {
      this.ws.onopen = () => resolve();
    });
  }
  
  async generateChart(content, options = {}) {
    const request = {
      message_id: `msg_${this.generateUUID()}`,
      correlation_id: `req_${this.generateUUID()}`,
      session_id: this.sessionId,
      type: "analytics_request",
      payload: { content, ...options }
    };
    
    this.ws.send(JSON.stringify(request));
  }
  
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }
}
```

### Python

```python
import asyncio
import json
import uuid
import websockets

async def generate_analytics():
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws?session_id={session_id}&user_id=python_client"
    
    async with websockets.connect(uri) as websocket:
        # Send request
        request = {
            "message_id": f"msg_{uuid.uuid4()}",
            "correlation_id": f"req_{uuid.uuid4()}",
            "session_id": session_id,
            "type": "analytics_request",
            "payload": {
                "content": "Show monthly sales trend",
                "use_synthetic_data": True
            }
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Chart generated: {data['payload']['metadata']['chart_type']}")

asyncio.run(generate_analytics())
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key for LLM features | Required |
| `PORT` | Service port | 8000 |
| `DEBUG_MODE` | Enable debug logging | false |
| `ENABLE_SYNTHETIC_DATA` | Allow synthetic data generation | true |
| `RATE_LIMIT_REQUESTS` | Requests per minute | 60 |
| `CORS_ORIGINS` | Allowed CORS origins | * |

## Architecture

This microservice follows a wrapper pattern where:
- **90%+ Code Reuse**: All analytics logic from `analytics_utils_v2` is preserved
- **WebSocket Layer**: Thin wrapper that translates messages
- **No Core Changes**: Analytics engine remains untouched
- **Simple Integration**: WebSocket → AnalyticsRequest → AnalyticsAgent → Response

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Statistics
```bash
curl http://localhost:8000/stats
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
```
analytics_microservice_v2/
├── analytics_utils_v2/     # Unchanged analytics engine (100% reused)
├── api/                    # WebSocket handlers
├── models/                 # WebSocket message models
├── config/                 # Configuration
├── main.py                # FastAPI application
└── requirements.txt       # Dependencies
```

## License

Copyright 2025 - Analytics Microservice V2

## Support

For issues or questions:
1. Check the documentation at `/docs`
2. Review health status at `/health`
3. Check stats at `/stats`

---

Built with ❤️ using FastAPI, WebSockets, and Pydantic AI