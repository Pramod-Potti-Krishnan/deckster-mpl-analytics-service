# Railway Deployment Test Suite

## Overview
This test suite validates the Analytics Microservice V2 deployed on Railway at:
- **URL**: `wss://deckster-mpl-analytics-service-production.up.railway.app/ws`

## Test Coverage
The suite tests 5 different chart types with real data:

1. **Line Chart** - Monthly revenue trend with 12 data points
2. **Bar Chart** - Product sales comparison with 5 categories  
3. **Pie Chart** - Market share distribution with 6 segments
4. **Scatter Plot** - Customer satisfaction vs sales with 20 data points
5. **Heatmap** - Weekly activity pattern with 7x24 matrix

## Running the Tests

### Prerequisites
```bash
pip install websockets asyncio
```

### Execute Tests
```bash
# Test Railway deployment (default)
python test_railway_deployment.py

# Test local deployment
# Edit the script and set USE_LOCAL = True, then run:
python test_railway_deployment.py
```

## Test Output

The test suite generates:

1. **Console Output** - Real-time test progress with colored status indicators
2. **railway_test_results.json** - Detailed test data and responses
3. **railway_test_results.html** - Visual report with all generated charts

## Viewing Results

Open `railway_test_results.html` in a web browser to see:
- All generated charts
- Chart metadata (titles, axes, configuration)
- AI-generated insights
- Test performance metrics
- Success/failure status for each test

## Test Features

Each test includes:
- Custom data points specific to the chart type
- Metadata with titles and descriptions
- Theme configuration (colors, styles)
- Enhanced labels using AI
- Performance timing

## Success Criteria

A test is considered successful if:
- WebSocket connection is established
- Request is processed without errors
- Response contains valid base64 chart image
- Response includes metadata and insights
- Response time is under 30 seconds

## Troubleshooting

If tests fail:
1. Check if the Railway deployment is active
2. Verify WebSocket connectivity
3. Check for any API key issues in Railway environment
4. Review error messages in console output
5. Check railway_test_results.json for detailed error information

## Sample Test Request

```json
{
  "message_id": "msg_123",
  "session_id": "session_456", 
  "type": "analytics_request",
  "payload": {
    "content": "Show monthly revenue trend",
    "title": "2024 Revenue Analysis",
    "data": [...],
    "chart_preference": "line_chart",
    "theme": {
      "color_palette": "modern"
    },
    "enhance_labels": true
  }
}
```

## Expected Response

```json
{
  "type": "analytics_response",
  "payload": {
    "chart_base64": "iVBORw0KGgo...",
    "metadata": {
      "title": "2024 Revenue Analysis",
      "chart_type": "line_chart",
      "x_label": "Month",
      "y_label": "Revenue ($)"
    },
    "insights": [
      "Revenue shows positive growth trend",
      "Peak performance in December"
    ],
    "table_data": {...}
  }
}
```