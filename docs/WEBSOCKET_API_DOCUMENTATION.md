# Analytics Microservice V2 - WebSocket API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Connection Setup](#connection-setup)
3. [Message Protocol](#message-protocol)
4. [Request Format](#request-format)
5. [Response Format](#response-format)
6. [Chart Types](#chart-types)
7. [Complete Examples](#complete-examples)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Integration Guide](#integration-guide)

---

## Overview

The Analytics Microservice V2 is a WebSocket-based service that generates professional data visualizations and analytics. It accepts natural language descriptions or structured data and returns:

- **PNG charts** as base64-encoded images
- **Comprehensive metadata** including titles, axis labels, and chart configuration
- **Table-ready data** formatted for direct display in HTML tables
- **Statistical insights** automatically generated from the data

### Key Features
- 🎨 **23 different chart types** from simple bar charts to complex Gantt charts
- 🤖 **AI-powered data synthesis** when no data is provided
- 🎯 **Intelligent chart selection** based on your description
- 📊 **Professional themes** with customizable colors
- 📈 **Statistical analysis** included with every response
- 🔄 **Real-time communication** via WebSocket

---

## Connection Setup

### WebSocket Endpoint
```
ws://[host]:[port]/ws?session_id=[uuid]&user_id=[string]
```

### Connection Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | UUID | Yes | Unique session identifier for this connection |
| `user_id` | String | Yes | User identifier for tracking and logging |

### Connection Example (JavaScript)
```javascript
const sessionId = crypto.randomUUID();
const userId = "client_app_123";
const ws = new WebSocket(`ws://localhost:8000/ws?session_id=${sessionId}&user_id=${userId}`);

ws.onopen = () => {
    console.log('Connected to Analytics Service');
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    handleResponse(response);
};
```

### Connection Example (Python)
```python
import asyncio
import websockets
import uuid
import json

async def connect():
    session_id = str(uuid.uuid4())
    user_id = "python_client"
    uri = f"ws://localhost:8000/ws?session_id={session_id}&user_id={user_id}"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection acknowledgment
        ack = await websocket.recv()
        print(f"Connected: {json.loads(ack)}")
        
        # Send analytics request
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        return json.loads(response)
```

---

## Message Protocol

### Message Flow
1. **Client connects** → Server sends connection acknowledgment
2. **Client sends request** → Server sends status updates
3. **Server processes** → Sends progress updates
4. **Server completes** → Sends final analytics response

### Message Types

#### From Server
| Type | Description |
|------|-------------|
| `connection_ack` | Confirms successful connection |
| `status` | Processing status updates |
| `analytics_response` | Final chart and data response |
| `error` | Error message if processing fails |
| `pong` | Response to ping keepalive |

#### From Client
| Type | Description |
|------|-------------|
| `analytics_request` | Request to generate analytics |
| `ping` | Keepalive message |

---

## Request Format

### Complete Request Structure
```json
{
    "message_id": "msg_unique_id",
    "correlation_id": "corr_unique_id",
    "session_id": "session_uuid",
    "type": "analytics_request",
    "timestamp": "2024-01-15T10:30:00Z",
    "payload": {
        "content": "Show quarterly sales trends for 2024",
        "title": "Q1-Q4 2024 Sales Analysis",
        "data": [...],
        "use_synthetic_data": true,
        "theme": {...},
        "chart_preference": "line_chart",
        "output_format": "png",
        "include_raw_data": true,
        "enhance_labels": true
    }
}
```

### Request Fields

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `message_id` | String | Unique identifier for this message |
| `type` | String | Must be "analytics_request" |
| `payload.content` | String | Natural language description of what to visualize |

#### Optional Payload Fields
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | String | Auto-generated | Chart title |
| `data` | Array | null | User-provided data points |
| `use_synthetic_data` | Boolean | true | Generate synthetic data if none provided |
| `theme` | Object | Default theme | Visual customization |
| `chart_preference` | String | Auto-selected | Preferred chart type |
| `output_format` | String | "png" | Output format (png/svg/base64) |
| `include_raw_data` | Boolean | true | Include data in response |
| `enhance_labels` | Boolean | true | Use AI to improve labels |

### Data Format
When providing your own data, use this structure:
```json
"data": [
    {"label": "January", "value": 45000},
    {"label": "February", "value": 52000},
    {"label": "March", "value": 48000}
]
```

For multi-series data:
```json
"data": [
    {"label": "Q1", "value": 45000, "series": "Product A"},
    {"label": "Q1", "value": 38000, "series": "Product B"},
    {"label": "Q2", "value": 52000, "series": "Product A"},
    {"label": "Q2", "value": 41000, "series": "Product B"}
]
```

### Theme Configuration
```json
"theme": {
    "primary": "#1E40AF",      // Primary color (hex)
    "secondary": "#10B981",     // Secondary color (hex)
    "tertiary": "#F59E0B",      // Tertiary color (hex)
    "style": "modern",          // modern/classic/minimal/dark/corporate
    "gradient": true,           // Use gradients
    "transparency": 0.8,        // 0-1 transparency level
    "font_family": "Arial",     // Font family
    "font_size": 12            // Base font size
}
```

---

## Response Format

### Complete Response Structure
```json
{
    "message_id": "msg_response_id",
    "correlation_id": "corr_unique_id",
    "session_id": "session_uuid",
    "type": "analytics_response",
    "timestamp": "2024-01-15T10:30:05Z",
    "payload": {
        "success": true,
        "chart": "iVBORw0KGgoAAAANS...",
        "metadata": {
            "chart_type": "line_chart",
            "title": "Q1-Q4 2024 Sales Analysis",
            "x_axis_label": "Quarter",
            "y_axis_label": "Revenue ($)",
            "x_axis_type": "temporal",
            "y_axis_type": "numerical",
            "generation_method": "python_mcp",
            "data_source": "synthetic",
            "generation_time_ms": 1250.5,
            "data_points_count": 12,
            "llm_enhanced": true,
            "timestamp": "2024-01-15T10:30:05Z",
            "insights": [
                "Data range: 38000 to 65000",
                "Average value: 48500",
                "Increasing trend detected"
            ],
            "theme_applied": {
                "primary": "#1E40AF",
                "secondary": "#10B981",
                "style": "modern"
            }
        },
        "data": {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [45000, 52000, 48000, 61000],
            "series": null,
            "categories": null,
            "statistics": {
                "min": 45000,
                "max": 61000,
                "mean": 51500,
                "median": 50000,
                "std": 6614.38,
                "total": 206000,
                "count": 4
            },
            "table_data": [
                {"Label": "Q1", "Value": 45000},
                {"Label": "Q2", "Value": 52000},
                {"Label": "Q3", "Value": 48000},
                {"Label": "Q4", "Value": 61000}
            ],
            "table_columns": ["Label", "Value"]
        }
    }
}
```

### Response Fields Explained

#### Payload Fields
| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Whether chart generation succeeded |
| `chart` | String | Base64-encoded PNG image |
| `metadata` | Object | Complete chart metadata |
| `data` | Object | Underlying data and statistics |
| `error` | String | Error message (only if success=false) |

#### Metadata Fields
| Field | Type | Description |
|-------|------|-------------|
| `chart_type` | String | Type of chart generated |
| `title` | String | Chart title |
| `x_axis_label` | String | Label for X-axis |
| `y_axis_label` | String | Label for Y-axis |
| `x_axis_type` | String | Type: categorical/numerical/temporal |
| `y_axis_type` | String | Type: numerical/percentage/count |
| `generation_time_ms` | Float | Time taken to generate (milliseconds) |
| `data_points_count` | Integer | Number of data points |
| `insights` | Array | Auto-generated insights about the data |

#### Data Fields
| Field | Type | Description |
|-------|------|-------------|
| `labels` | Array | X-axis labels |
| `values` | Array | Y-axis values |
| `statistics` | Object | Statistical summary |
| `table_data` | Array | Data formatted for table display |
| `table_columns` | Array | Column names for table |

---

## Chart Types

### Available Chart Types (23 Total)

#### Line and Trend Charts
| Type | ID | Best For |
|------|-----|----------|
| Line Chart | `line_chart` | Trends over time |
| Step Chart | `step_chart` | Discrete changes |
| Area Chart | `area_chart` | Volume over time |
| Stacked Area | `stacked_area_chart` | Composition over time |

#### Bar Charts
| Type | ID | Best For |
|------|-----|----------|
| Vertical Bar | `bar_chart_vertical` | Comparing categories |
| Horizontal Bar | `bar_chart_horizontal` | Long category names |
| Grouped Bar | `grouped_bar_chart` | Multiple series comparison |
| Stacked Bar | `stacked_bar_chart` | Part-to-whole relationships |

#### Distribution Charts
| Type | ID | Best For |
|------|-----|----------|
| Histogram | `histogram` | Frequency distribution |
| Box Plot | `box_plot` | Statistical quartiles |
| Violin Plot | `violin_plot` | Distribution shape |

#### Correlation Charts
| Type | ID | Best For |
|------|-----|----------|
| Scatter Plot | `scatter_plot` | Correlation between variables |
| Bubble Chart | `bubble_chart` | Three-dimensional data |
| Hexbin | `hexbin` | Dense scatter data |

#### Composition Charts
| Type | ID | Best For |
|------|-----|----------|
| Pie Chart | `pie_chart` | Proportions of a whole |
| Waterfall | `waterfall` | Cumulative effect |
| Funnel | `funnel` | Process stages |

#### Comparison Charts
| Type | ID | Best For |
|------|-----|----------|
| Radar Chart | `radar_chart` | Multi-dimensional comparison |
| Heatmap | `heatmap` | Matrix visualization |

#### Statistical Charts
| Type | ID | Best For |
|------|-----|----------|
| Error Bar | `error_bar_chart` | Confidence intervals |
| Control Chart | `control_chart` | Process monitoring |
| Pareto | `pareto` | 80/20 analysis |

#### Project Charts
| Type | ID | Best For |
|------|-----|----------|
| Gantt Chart | `gantt` | Project timelines |

---

## Complete Examples

### Example 1: Simple Bar Chart with Synthetic Data
**Request:**
```json
{
    "message_id": "msg_001",
    "correlation_id": "corr_001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "analytics_request",
    "timestamp": "2024-01-15T10:00:00Z",
    "payload": {
        "content": "Show top 5 product sales for Q1 2024",
        "title": "Q1 2024 Product Sales",
        "use_synthetic_data": true,
        "chart_preference": "bar_chart_vertical"
    }
}
```

**Response:**
```json
{
    "type": "analytics_response",
    "payload": {
        "success": true,
        "chart": "iVBORw0KGgoAAAANS...",
        "metadata": {
            "chart_type": "bar_chart_vertical",
            "title": "Q1 2024 Product Sales",
            "x_axis_label": "Product",
            "y_axis_label": "Sales ($)",
            "x_axis_type": "categorical",
            "y_axis_type": "numerical",
            "data_points_count": 5
        },
        "data": {
            "labels": ["Product A", "Product B", "Product C", "Product D", "Product E"],
            "values": [45000, 38000, 52000, 41000, 35000],
            "table_data": [
                {"Label": "Product A", "Value": 45000},
                {"Label": "Product B", "Value": 38000},
                {"Label": "Product C", "Value": 52000},
                {"Label": "Product D", "Value": 41000},
                {"Label": "Product E", "Value": 35000}
            ],
            "table_columns": ["Label", "Value"]
        }
    }
}
```

### Example 2: Multi-Series Line Chart with User Data
**Request:**
```json
{
    "message_id": "msg_002",
    "type": "analytics_request",
    "payload": {
        "content": "Compare monthly revenue for products A and B",
        "title": "Product Revenue Comparison",
        "data": [
            {"label": "Jan", "value": 30000, "series": "Product A"},
            {"label": "Jan", "value": 25000, "series": "Product B"},
            {"label": "Feb", "value": 35000, "series": "Product A"},
            {"label": "Feb", "value": 28000, "series": "Product B"},
            {"label": "Mar", "value": 40000, "series": "Product A"},
            {"label": "Mar", "value": 32000, "series": "Product B"}
        ],
        "chart_preference": "line_chart"
    }
}
```

**Response:**
```json
{
    "type": "analytics_response",
    "payload": {
        "success": true,
        "chart": "iVBORw0KGgoAAAANS...",
        "metadata": {
            "chart_type": "line_chart",
            "title": "Product Revenue Comparison",
            "x_axis_label": "Month",
            "y_axis_label": "Revenue ($)",
            "x_axis_type": "temporal",
            "y_axis_type": "numerical",
            "data_points_count": 6
        },
        "data": {
            "labels": ["Jan", "Feb", "Mar"],
            "series": [
                {
                    "name": "Product A",
                    "data": [
                        {"label": "Jan", "value": 30000},
                        {"label": "Feb", "value": 35000},
                        {"label": "Mar", "value": 40000}
                    ]
                },
                {
                    "name": "Product B",
                    "data": [
                        {"label": "Jan", "value": 25000},
                        {"label": "Feb", "value": 28000},
                        {"label": "Mar", "value": 32000}
                    ]
                }
            ],
            "table_data": [
                {"Label": "Jan", "Product A": 30000, "Product B": 25000},
                {"Label": "Feb", "Product A": 35000, "Product B": 28000},
                {"Label": "Mar", "Product A": 40000, "Product B": 32000}
            ],
            "table_columns": ["Label", "Product A", "Product B"]
        }
    }
}
```

### Example 3: Custom Themed Pie Chart
**Request:**
```json
{
    "message_id": "msg_003",
    "type": "analytics_request",
    "payload": {
        "content": "Market share distribution for Q4 2024",
        "title": "Q4 2024 Market Share",
        "chart_preference": "pie_chart",
        "theme": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "tertiary": "#45B7D1",
            "style": "modern",
            "gradient": true
        }
    }
}
```

---

## Error Handling

### Error Response Format
```json
{
    "type": "error",
    "payload": {
        "code": "INVALID_REQUEST",
        "message": "Missing required field: content",
        "details": {
            "field": "payload.content",
            "requirement": "This field is required"
        }
    }
}
```

### Common Error Codes
| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_REQUEST` | Request format is invalid | Check required fields |
| `UNSUPPORTED_CHART` | Chart type not supported | Use valid chart_type |
| `DATA_ERROR` | Problem with provided data | Verify data format |
| `GENERATION_FAILED` | Chart generation failed | Retry or simplify request |
| `RATE_LIMIT` | Too many requests | Wait before retrying |
| `TIMEOUT` | Processing timeout | Simplify request |

### Error Handling Best Practices
1. Always check `success` field in response
2. Implement exponential backoff for retries
3. Log correlation_id for debugging
4. Provide fallback UI for errors
5. Validate data before sending

---

## Rate Limiting

### Limits
- **Requests per minute**: 60
- **Concurrent connections**: 100
- **Max message size**: 1MB
- **Connection timeout**: 5 minutes idle

### Rate Limit Response
```json
{
    "type": "error",
    "payload": {
        "code": "RATE_LIMIT",
        "message": "Rate limit exceeded",
        "retry_after": 30
    }
}
```

---

## Integration Guide

### JavaScript/TypeScript Integration
```typescript
class AnalyticsClient {
    private ws: WebSocket;
    private sessionId: string;
    private messageQueue: Map<string, (response: any) => void>;

    constructor(host: string, port: number, userId: string) {
        this.sessionId = crypto.randomUUID();
        this.messageQueue = new Map();
        this.connect(host, port, userId);
    }

    private connect(host: string, port: number, userId: string) {
        const url = `ws://${host}:${port}/ws?session_id=${this.sessionId}&user_id=${userId}`;
        this.ws = new WebSocket(url);

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'analytics_response') {
                const handler = this.messageQueue.get(message.correlation_id);
                if (handler) {
                    handler(message.payload);
                    this.messageQueue.delete(message.correlation_id);
                }
            }
        };
    }

    async generateChart(content: string, options?: any): Promise<any> {
        return new Promise((resolve) => {
            const messageId = crypto.randomUUID();
            const correlationId = crypto.randomUUID();

            this.messageQueue.set(correlationId, resolve);

            const request = {
                message_id: messageId,
                correlation_id: correlationId,
                session_id: this.sessionId,
                type: 'analytics_request',
                timestamp: new Date().toISOString(),
                payload: {
                    content,
                    ...options
                }
            };

            this.ws.send(JSON.stringify(request));
        });
    }

    displayChart(response: any) {
        if (response.success) {
            // Display the chart
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${response.chart}`;
            
            // Display metadata
            console.log('Chart Title:', response.metadata.title);
            console.log('Chart Type:', response.metadata.chart_type);
            
            // Display as table
            this.renderTable(response.data.table_data, response.data.table_columns);
        }
    }

    renderTable(data: any[], columns: string[]) {
        const table = document.createElement('table');
        
        // Create header
        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        
        // Create body
        const tbody = table.createTBody();
        data.forEach(row => {
            const tr = tbody.insertRow();
            columns.forEach(col => {
                const td = tr.insertCell();
                td.textContent = row[col];
            });
        });
        
        document.body.appendChild(table);
    }
}

// Usage
const client = new AnalyticsClient('localhost', 8000, 'web_app');
const response = await client.generateChart(
    'Show monthly sales trends',
    { title: 'Sales Trends 2024' }
);
client.displayChart(response);
```

### Python Integration
```python
import asyncio
import websockets
import json
import uuid
from typing import Dict, Any, Optional
import base64
from PIL import Image
from io import BytesIO

class AnalyticsClient:
    def __init__(self, host: str = 'localhost', port: int = 8000, user_id: str = 'python_client'):
        self.host = host
        self.port = port
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        
    async def generate_chart(
        self, 
        content: str, 
        title: Optional[str] = None,
        data: Optional[list] = None,
        chart_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chart using the analytics service."""
        
        uri = f"ws://{self.host}:{self.port}/ws?session_id={self.session_id}&user_id={self.user_id}"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection ack
            ack = await websocket.recv()
            
            # Prepare request
            request = {
                "message_id": f"msg_{uuid.uuid4()}",
                "correlation_id": f"corr_{uuid.uuid4()}",
                "session_id": self.session_id,
                "type": "analytics_request",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "content": content,
                    "title": title,
                    "data": data,
                    "chart_preference": chart_type,
                    **kwargs
                }
            }
            
            # Send request
            await websocket.send(json.dumps(request))
            
            # Collect responses
            while True:
                response = await websocket.recv()
                message = json.loads(response)
                
                if message['type'] == 'analytics_response':
                    return message['payload']
                elif message['type'] == 'error':
                    raise Exception(f"Error: {message['payload']['message']}")
    
    def save_chart(self, response: Dict[str, Any], filename: str):
        """Save the chart image to a file."""
        if response['success'] and response['chart']:
            # Decode base64 image
            image_data = base64.b64decode(response['chart'])
            image = Image.open(BytesIO(image_data))
            image.save(filename)
            print(f"Chart saved to {filename}")
    
    def display_data_as_table(self, response: Dict[str, Any]):
        """Display the data as a formatted table."""
        if response['success'] and response['data']['table_data']:
            import pandas as pd
            
            df = pd.DataFrame(response['data']['table_data'])
            print(f"\n{response['metadata']['title']}")
            print("=" * 50)
            print(df.to_string(index=False))
            print("\nStatistics:")
            for key, value in response['data']['statistics'].items():
                print(f"  {key}: {value}")

# Usage example
async def main():
    client = AnalyticsClient()
    
    # Generate chart with synthetic data
    response = await client.generate_chart(
        content="Show quarterly revenue for 2024",
        title="2024 Revenue by Quarter"
    )
    
    # Save the chart
    client.save_chart(response, "revenue_chart.png")
    
    # Display as table
    client.display_data_as_table(response)
    
    # Generate with custom data
    custom_data = [
        {"label": "Q1", "value": 100000},
        {"label": "Q2", "value": 120000},
        {"label": "Q3", "value": 95000},
        {"label": "Q4", "value": 140000}
    ]
    
    response = await client.generate_chart(
        content="Quarterly performance",
        data=custom_data,
        chart_type="bar_chart_vertical"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### React Integration
```jsx
import React, { useState, useEffect } from 'react';

const AnalyticsChart = ({ content, title, data, chartType }) => {
    const [chart, setChart] = useState(null);
    const [metadata, setMetadata] = useState(null);
    const [tableData, setTableData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const generateChart = async () => {
            setLoading(true);
            setError(null);

            const sessionId = crypto.randomUUID();
            const ws = new WebSocket(
                `ws://localhost:8000/ws?session_id=${sessionId}&user_id=react_app`
            );

            ws.onopen = () => {
                const request = {
                    message_id: crypto.randomUUID(),
                    correlation_id: crypto.randomUUID(),
                    session_id: sessionId,
                    type: 'analytics_request',
                    timestamp: new Date().toISOString(),
                    payload: {
                        content,
                        title,
                        data,
                        chart_preference: chartType
                    }
                };
                ws.send(JSON.stringify(request));
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                
                if (message.type === 'analytics_response') {
                    const response = message.payload;
                    if (response.success) {
                        setChart(`data:image/png;base64,${response.chart}`);
                        setMetadata(response.metadata);
                        setTableData({
                            data: response.data.table_data,
                            columns: response.data.table_columns
                        });
                    } else {
                        setError(response.error);
                    }
                    setLoading(false);
                    ws.close();
                }
            };

            ws.onerror = (err) => {
                setError('Connection failed');
                setLoading(false);
            };
        };

        if (content) {
            generateChart();
        }
    }, [content, title, data, chartType]);

    if (loading) return <div>Generating chart...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!chart) return null;

    return (
        <div className="analytics-container">
            <h2>{metadata?.title}</h2>
            
            <div className="chart-section">
                <img src={chart} alt={metadata?.title} />
                <div className="chart-info">
                    <p>Type: {metadata?.chart_type}</p>
                    <p>Data Points: {metadata?.data_points_count}</p>
                    <p>Generation Time: {metadata?.generation_time_ms}ms</p>
                </div>
            </div>

            {tableData && (
                <div className="table-section">
                    <h3>Data Table</h3>
                    <table>
                        <thead>
                            <tr>
                                {tableData.columns.map(col => (
                                    <th key={col}>{col}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.data.map((row, i) => (
                                <tr key={i}>
                                    {tableData.columns.map(col => (
                                        <td key={col}>{row[col]}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {metadata?.insights && (
                <div className="insights-section">
                    <h3>Insights</h3>
                    <ul>
                        {metadata.insights.map((insight, i) => (
                            <li key={i}>{insight}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default AnalyticsChart;
```

---

## Best Practices

### Do's ✅
1. **Reuse WebSocket connections** for multiple requests
2. **Include correlation_id** for request tracking
3. **Validate data format** before sending
4. **Handle all message types** (status, error, response)
5. **Implement reconnection logic** for dropped connections
6. **Cache charts** when appropriate
7. **Use table_data** for accessible data display

### Don'ts ❌
1. **Don't send** requests larger than 1MB
2. **Don't ignore** status messages
3. **Don't create** new connections for each request
4. **Don't assume** immediate responses
5. **Don't hardcode** session IDs
6. **Don't skip** error handling

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Connection refused | Service not running | Check if service is running on correct port |
| No response | Missing required fields | Verify request includes all required fields |
| Chart is null | Generation failed | Check error field in response |
| Wrong chart type | Auto-selection issue | Specify chart_preference explicitly |
| Data not displayed | Format issue | Verify data matches expected structure |
| Timeout errors | Complex request | Simplify request or increase timeout |

### Debug Mode
Add `debug: true` to your request payload for verbose logging:
```json
{
    "payload": {
        "content": "...",
        "debug": true
    }
}
```

---

## Appendix

### Status Message Format
```json
{
    "type": "status",
    "payload": {
        "status": "processing",
        "message": "Generating chart...",
        "progress": 0.5
    }
}
```

### Ping/Pong Keepalive
```json
// Client sends
{"type": "ping"}

// Server responds
{"type": "pong"}
```

### Connection Acknowledgment
```json
{
    "type": "connection_ack",
    "payload": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "Connected successfully"
    }
}
```

---

## Contact & Support

For issues, feature requests, or questions:
- GitHub: [Analytics Microservice V2 Repository]
- Documentation: This document
- Version: 2.0.0

---

*Last Updated: January 2025*