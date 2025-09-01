# Analytics Microservice V2 Documentation

Welcome to the comprehensive documentation for the Analytics Microservice V2 - a powerful WebSocket-based service for generating professional data visualizations.

## 📚 Documentation Structure

### 1. [Quick Start Guide](./QUICK_START_GUIDE.md)
**Start Here!** Get your first chart generated in under 5 minutes.
- Simple connection examples
- Minimal requests
- Copy-paste code snippets
- Troubleshooting tips

### 2. [WebSocket API Documentation](./WEBSOCKET_API_DOCUMENTATION.md)
**Complete API Reference** - Everything you need to integrate the service.
- Connection setup and protocol
- Request/response formats
- All fields explained
- Error handling
- Rate limiting
- Integration examples for multiple languages

### 3. [Chart Types Guide](./CHART_TYPES_GUIDE.md)
**Visual Analytics Catalog** - Detailed guide to all 23 chart types.
- When to use each chart type
- Best practices
- Industry-specific examples
- Chart selection guide

---

## 🎯 Service Overview

The Analytics Microservice V2 is a **black-box service** that:

### Accepts
- Natural language descriptions of what you want to visualize
- Optional structured data in JSON format
- Chart preferences and customization options

### Returns
- **PNG charts** as base64-encoded images
- **Complete metadata** including titles, axis labels, and configuration
- **Table-ready data** formatted for direct HTML display
- **Statistical insights** automatically generated

---

## 🚀 Key Features

### 📊 23 Chart Types
From simple bar charts to complex Gantt charts - full variety for any visualization need.

### 🤖 AI-Powered
- Automatic chart type selection
- Synthetic data generation when needed
- Intelligent label enhancement
- Statistical insights generation

### 🎨 Professional Themes
- Multiple style presets
- Customizable colors
- Gradient support
- Responsive sizing

### 📈 Data Flexibility
- Works with or without data
- Handles single and multi-series
- Supports categorical, numerical, and temporal data
- Automatic statistical analysis

### 🔌 Easy Integration
- WebSocket for real-time communication
- Language-agnostic JSON protocol
- Status updates during processing
- Comprehensive error messages

---

## 💻 Integration Examples

### Minimal Request
```json
{
    "message_id": "msg_001",
    "type": "analytics_request",
    "payload": {
        "content": "Show monthly sales for 2024"
    }
}
```

### With Custom Data
```json
{
    "message_id": "msg_002",
    "type": "analytics_request",
    "payload": {
        "content": "Visualize quarterly performance",
        "data": [
            {"label": "Q1", "value": 45000},
            {"label": "Q2", "value": 52000},
            {"label": "Q3", "value": 48000},
            {"label": "Q4", "value": 61000}
        ]
    }
}
```

### Full Customization
```json
{
    "message_id": "msg_003",
    "type": "analytics_request",
    "payload": {
        "content": "Compare regional sales performance",
        "title": "Regional Sales Analysis",
        "chart_preference": "grouped_bar_chart",
        "theme": {
            "primary": "#1E40AF",
            "style": "modern"
        },
        "enhance_labels": true
    }
}
```

---

## 📝 Response Format

Every successful response includes:

```json
{
    "type": "analytics_response",
    "payload": {
        "success": true,
        "chart": "base64_png_image...",
        "metadata": {
            "title": "Chart Title",
            "chart_type": "bar_chart_vertical",
            "x_axis_label": "Category",
            "y_axis_label": "Value",
            "insights": ["Key insight 1", "Key insight 2"]
        },
        "data": {
            "table_data": [...],
            "table_columns": [...],
            "statistics": {...}
        }
    }
}
```

---

## 🛠️ Use Cases

### Business Intelligence
- Sales dashboards
- Performance metrics
- Financial reports
- Market analysis

### Data Science
- Statistical distributions
- Correlation analysis
- Time series analysis
- Experimental results

### Project Management
- Gantt charts
- Resource allocation
- Progress tracking
- Timeline visualization

### Marketing
- Conversion funnels
- Campaign performance
- Customer segmentation
- A/B test results

---

## 🔧 Technical Requirements

### Client Requirements
- WebSocket support
- JSON parsing capability
- Base64 decoding for images

### Network Requirements
- Stable WebSocket connection
- Port 8000 (default) accessibility
- Message size < 1MB

### Recommended Libraries
- **JavaScript**: Native WebSocket API
- **Python**: websockets library
- **Node.js**: ws package
- **React**: Native or socket.io-client

---

## 📊 Supported Data Formats

### Simple Data
```json
[
    {"label": "A", "value": 10},
    {"label": "B", "value": 20}
]
```

### Multi-Series Data
```json
[
    {"label": "Jan", "value": 100, "series": "Product A"},
    {"label": "Jan", "value": 150, "series": "Product B"}
]
```

### Grouped Data
```json
[
    {"label": "North", "value": 1000, "category": "Q1"},
    {"label": "North", "value": 1200, "category": "Q2"}
]
```

---

## 🎯 Quick Decision Guide

### Choose This Service If You Need:
✅ Quick chart generation from descriptions  
✅ Professional visualizations without coding  
✅ Automatic data synthesis for prototypes  
✅ Multiple chart types from single API  
✅ Real-time chart generation  
✅ Table and chart data together  

### Consider Alternatives If You Need:
❌ Interactive charts (D3.js, Plotly)  
❌ Real-time streaming updates  
❌ Complex custom visualizations  
❌ Client-side only solution  
❌ Offline operation  

---

## 📞 Support & Feedback

For questions, issues, or feature requests:
- Review the documentation sections
- Check the troubleshooting guides
- Test with the Quick Start examples

---

## 🚦 Service Status Indicators

| Status | Meaning |
|--------|---------|
| 🟢 Connected | WebSocket connection established |
| 🟡 Processing | Chart generation in progress |
| 🟢 Success | Chart generated successfully |
| 🔴 Error | Generation failed (check error message) |

---

## 📈 Performance Metrics

- **Average generation time**: 1-2 seconds
- **Success rate**: >95%
- **Supported concurrent connections**: 100
- **Max request size**: 1MB
- **Chart resolution**: 800x600px default

---

## 🔄 Version Information

**Current Version**: 2.0.0  
**Protocol Version**: WebSocket  
**API Version**: v2  
**Last Updated**: January 2025  

---

*Start with the [Quick Start Guide](./QUICK_START_GUIDE.md) to begin using the service immediately!*