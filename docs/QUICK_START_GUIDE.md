# Analytics Microservice V2 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you generate your first chart using the Analytics Microservice V2.

---

## Prerequisites

- WebSocket client (browser, Python, Node.js, etc.)
- Service running on `ws://localhost:8000` (or your deployment URL)

---

## Step 1: Connect to the Service

### Browser Console (Simplest)
```javascript
// Open browser console and paste:
const ws = new WebSocket('ws://localhost:8000/ws?session_id=' + crypto.randomUUID() + '&user_id=quickstart');
```

### Python
```python
import websockets
import uuid
uri = f"ws://localhost:8000/ws?session_id={uuid.uuid4()}&user_id=quickstart"
```

---

## Step 2: Send Your First Request

### Minimal Request (AI generates everything)
```json
{
    "message_id": "msg_001",
    "type": "analytics_request",
    "payload": {
        "content": "Show monthly sales for 2024"
    }
}
```

The service will:
- ✅ Auto-select the best chart type
- ✅ Generate synthetic data
- ✅ Create professional labels
- ✅ Apply default theme
- ✅ Generate a title

### Simple Request with Title
```json
{
    "message_id": "msg_002",
    "type": "analytics_request",
    "payload": {
        "content": "Compare revenue across product categories",
        "title": "Product Revenue Comparison"
    }
}
```

### Request with Your Data
```json
{
    "message_id": "msg_003",
    "type": "analytics_request",
    "payload": {
        "content": "Visualize this data",
        "data": [
            {"label": "Q1", "value": 45000},
            {"label": "Q2", "value": 52000},
            {"label": "Q3", "value": 48000},
            {"label": "Q4", "value": 61000}
        ]
    }
}
```

---

## Step 3: Handle the Response

### What You'll Receive
```json
{
    "type": "analytics_response",
    "payload": {
        "success": true,
        "chart": "iVBORw0KGgoAAAANS...",  // Base64 PNG image
        "metadata": {
            "title": "Monthly Sales 2024",
            "chart_type": "line_chart",
            "x_axis_label": "Month",
            "y_axis_label": "Sales ($)"
        },
        "data": {
            "table_data": [...],  // Ready for HTML table
            "statistics": {...}   // Min, max, mean, etc.
        }
    }
}
```

### Display the Chart (HTML)
```html
<img id="chart" />
<script>
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    if (response.type === 'analytics_response' && response.payload.success) {
        document.getElementById('chart').src = 
            'data:image/png;base64,' + response.payload.chart;
    }
};
</script>
```

---

## Complete Working Examples

### 1. Browser Example (Copy & Paste)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Analytics Quick Start</title>
</head>
<body>
    <h1>My First Chart</h1>
    <button onclick="generateChart()">Generate Chart</button>
    <div id="result">
        <img id="chart" style="max-width: 800px;" />
        <div id="metadata"></div>
    </div>

    <script>
    let ws;
    
    function connect() {
        const sessionId = crypto.randomUUID();
        ws = new WebSocket(`ws://localhost:8000/ws?session_id=${sessionId}&user_id=browser`);
        
        ws.onopen = () => console.log('Connected!');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            
            if (msg.type === 'analytics_response') {
                const response = msg.payload;
                if (response.success) {
                    // Display chart
                    document.getElementById('chart').src = 
                        'data:image/png;base64,' + response.chart;
                    
                    // Display metadata
                    document.getElementById('metadata').innerHTML = `
                        <h3>${response.metadata.title}</h3>
                        <p>Chart Type: ${response.metadata.chart_type}</p>
                        <p>Data Points: ${response.metadata.data_points_count}</p>
                    `;
                }
            }
        };
    }
    
    function generateChart() {
        const request = {
            message_id: crypto.randomUUID(),
            type: 'analytics_request',
            payload: {
                content: 'Show top 5 products by revenue',
                title: 'Top Products'
            }
        };
        ws.send(JSON.stringify(request));
    }
    
    // Connect on load
    connect();
    </script>
</body>
</html>
```

### 2. Python Example (Save & Run)
```python
# save as: quick_chart.py
import asyncio
import websockets
import json
import uuid
from datetime import datetime

async def generate_chart():
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws?session_id={session_id}&user_id=python"
    
    async with websockets.connect(uri) as ws:
        # Wait for connection
        ack = await ws.recv()
        print("Connected!")
        
        # Send request
        request = {
            "message_id": f"msg_{uuid.uuid4()}",
            "type": "analytics_request",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "content": "Show quarterly sales trend",
                "title": "Q1-Q4 Sales"
            }
        }
        
        await ws.send(json.dumps(request))
        print("Request sent!")
        
        # Get response
        while True:
            response = await ws.recv()
            msg = json.loads(response)
            
            if msg['type'] == 'analytics_response':
                if msg['payload']['success']:
                    print(f"✅ Chart generated!")
                    print(f"Title: {msg['payload']['metadata']['title']}")
                    print(f"Type: {msg['payload']['metadata']['chart_type']}")
                    
                    # Save chart
                    import base64
                    img_data = base64.b64decode(msg['payload']['chart'])
                    with open('chart.png', 'wb') as f:
                        f.write(img_data)
                    print("Chart saved as chart.png")
                break

if __name__ == "__main__":
    asyncio.run(generate_chart())
```

### 3. Node.js Example
```javascript
// save as: quick_chart.js
const WebSocket = require('ws');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const sessionId = uuidv4();
const ws = new WebSocket(`ws://localhost:8000/ws?session_id=${sessionId}&user_id=nodejs`);

ws.on('open', () => {
    console.log('Connected!');
    
    const request = {
        message_id: uuidv4(),
        type: 'analytics_request',
        payload: {
            content: 'Show customer distribution by region',
            title: 'Regional Distribution'
        }
    };
    
    ws.send(JSON.stringify(request));
    console.log('Request sent!');
});

ws.on('message', (data) => {
    const msg = JSON.parse(data);
    
    if (msg.type === 'analytics_response' && msg.payload.success) {
        console.log('✅ Chart generated!');
        console.log(`Title: ${msg.payload.metadata.title}`);
        
        // Save chart
        const buffer = Buffer.from(msg.payload.chart, 'base64');
        fs.writeFileSync('chart.png', buffer);
        console.log('Chart saved as chart.png');
        
        ws.close();
    }
});
```

---

## Common Patterns

### 1. Bar Chart with Categories
```json
{
    "payload": {
        "content": "Sales by product category",
        "chart_preference": "bar_chart_vertical"
    }
}
```

### 2. Time Series Line Chart
```json
{
    "payload": {
        "content": "Monthly revenue trend for 2024",
        "chart_preference": "line_chart"
    }
}
```

### 3. Pie Chart for Proportions
```json
{
    "payload": {
        "content": "Market share distribution",
        "chart_preference": "pie_chart"
    }
}
```

### 4. Scatter Plot for Correlation
```json
{
    "payload": {
        "content": "Relationship between price and demand",
        "chart_preference": "scatter_plot"
    }
}
```

### 5. Multi-Series Comparison
```json
{
    "payload": {
        "content": "Compare sales of products A, B, and C over time",
        "data": [
            {"label": "Jan", "value": 100, "series": "Product A"},
            {"label": "Jan", "value": 150, "series": "Product B"},
            {"label": "Jan", "value": 120, "series": "Product C"}
        ]
    }
}
```

---

## Response Handling Tips

### 1. Check Success
```javascript
if (response.payload.success) {
    // Display chart
} else {
    console.error(response.payload.error);
}
```

### 2. Display as Image
```javascript
const img = document.createElement('img');
img.src = 'data:image/png;base64,' + response.payload.chart;
```

### 3. Use Table Data
```javascript
const tableData = response.payload.data.table_data;
const columns = response.payload.data.table_columns;
// Create HTML table with this data
```

### 4. Show Insights
```javascript
response.payload.metadata.insights.forEach(insight => {
    console.log('💡 ' + insight);
});
```

---

## Customization Options

### Custom Theme
```json
{
    "payload": {
        "content": "...",
        "theme": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "style": "modern"
        }
    }
}
```

### Specific Chart Type
```json
{
    "payload": {
        "content": "...",
        "chart_preference": "grouped_bar_chart"
    }
}
```

### Disable AI Enhancement
```json
{
    "payload": {
        "content": "...",
        "enhance_labels": false,
        "use_synthetic_data": false
    }
}
```

---

## What's Next?

1. 📖 Read the [Full API Documentation](./WEBSOCKET_API_DOCUMENTATION.md)
2. 🎨 Explore all [23 Chart Types](./CHART_TYPES_GUIDE.md)
3. 🔧 Check [Integration Examples](./INTEGRATION_EXAMPLES.md)
4. 🚀 Deploy to production

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure service is running on port 8000 |
| No response | Check if request has required fields |
| Chart is null | Look for error message in response |
| Wrong chart type | Explicitly set chart_preference |

---

## Need Help?

- Check the full documentation
- Review example code
- Ensure all required fields are present
- Verify WebSocket connection is established

---

*Happy Charting! 📊*