#!/usr/bin/env python3
"""
Railway Deployment Test Script for Analytics Microservice V2

Tests the deployed service at deckster-mpl-analytics-service-production.up.railway.app
with 5 different chart types including custom data and metadata.

Author: Analytics Test Suite
Date: 2025-09-01
"""

import asyncio
import websockets
import json
import uuid
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os
import ssl

# Configuration
RAILWAY_URL = "wss://deckster-mpl-analytics-service-production.up.railway.app/ws"
LOCAL_URL = "ws://localhost:8000/ws"  # For local testing
USE_LOCAL = False  # Set to True for local testing

# Select the appropriate URL
WS_URL = LOCAL_URL if USE_LOCAL else RAILWAY_URL

# Test configuration
TEST_TIMEOUT = 30  # seconds per test
SAVE_RESULTS = True

# ANSI color codes for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")


def print_test(test_name: str):
    """Print test name"""
    print(f"\n{Colors.CYAN}▶ Testing: {test_name}{Colors.ENDC}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")


# Test cases with 5 different chart types
TEST_CASES = [
    {
        "name": "Line Chart - Monthly Revenue Trend",
        "request": {
            "content": "Show monthly revenue trend for 2024 with growth indicators",
            "title": "2024 Monthly Revenue Analysis",
            "data": [
                {"label": "Jan", "value": 125000, "series": "revenue"},
                {"label": "Jan", "value": 120000, "series": "target"},
                {"label": "Feb", "value": 135000, "series": "revenue"},
                {"label": "Feb", "value": 130000, "series": "target"},
                {"label": "Mar", "value": 142000, "series": "revenue"},
                {"label": "Mar", "value": 140000, "series": "target"},
                {"label": "Apr", "value": 138000, "series": "revenue"},
                {"label": "Apr", "value": 145000, "series": "target"},
                {"label": "May", "value": 155000, "series": "revenue"},
                {"label": "May", "value": 150000, "series": "target"},
                {"label": "Jun", "value": 168000, "series": "revenue"},
                {"label": "Jun", "value": 160000, "series": "target"},
                {"label": "Jul", "value": 175000, "series": "revenue"},
                {"label": "Jul", "value": 170000, "series": "target"},
                {"label": "Aug", "value": 182000, "series": "revenue"},
                {"label": "Aug", "value": 175000, "series": "target"},
                {"label": "Sep", "value": 195000, "series": "revenue"},
                {"label": "Sep", "value": 185000, "series": "target"},
                {"label": "Oct", "value": 205000, "series": "revenue"},
                {"label": "Oct", "value": 195000, "series": "target"},
                {"label": "Nov", "value": 218000, "series": "revenue"},
                {"label": "Nov", "value": 210000, "series": "target"},
                {"label": "Dec", "value": 230000, "series": "revenue"},
                {"label": "Dec", "value": 220000, "series": "target"}
            ],
            "chart_preference": "line_chart",
            "theme": {
                "primary": "#2563EB",
                "secondary": "#10B981",
                "style": "modern"
            },
            "enhance_labels": True
        }
    },
    {
        "name": "Bar Chart - Product Sales Comparison",
        "request": {
            "content": "Compare Q4 2024 sales performance across product categories",
            "title": "Q4 2024 Product Category Performance",
            "data": [
                {"label": "Electronics", "value": 450000},
                {"label": "Clothing", "value": 320000},
                {"label": "Home & Garden", "value": 280000},
                {"label": "Sports & Outdoors", "value": 195000},
                {"label": "Books & Media", "value": 125000}
            ],
            "chart_preference": "bar_chart_vertical",
            "theme": {
                "primary": "#8B5CF6",
                "secondary": "#EC4899",
                "style": "modern"
            },
            "enhance_labels": True
        }
    },
    {
        "name": "Pie Chart - Market Share Distribution",
        "request": {
            "content": "Display market share distribution for cloud providers in 2024",
            "title": "Cloud Market Share 2024",
            "data": [
                {"label": "AWS", "value": 32.5},
                {"label": "Azure", "value": 23.8},
                {"label": "Google Cloud", "value": 11.2},
                {"label": "Alibaba Cloud", "value": 8.3},
                {"label": "IBM Cloud", "value": 4.7},
                {"label": "Others", "value": 19.5}
            ],
            "chart_preference": "pie_chart",
            "theme": {
                "primary": "#FF6600",
                "secondary": "#146EB4",
                "tertiary": "#232F3E",
                "style": "classic"
            },
            "enhance_labels": True
        }
    },
    {
        "name": "Scatter Plot - Customer Satisfaction vs Purchase Value",
        "request": {
            "content": "Analyze correlation between customer satisfaction scores and purchase values",
            "title": "Customer Satisfaction vs Purchase Value Analysis",
            "data": [
                {"label": "C001", "value": 1250, "x": 4.8},
                {"label": "C002", "value": 450, "x": 3.2},
                {"label": "C003", "value": 980, "x": 4.5},
                {"label": "C004", "value": 320, "x": 2.8},
                {"label": "C005", "value": 1580, "x": 4.9},
                {"label": "C006", "value": 670, "x": 3.7},
                {"label": "C007", "value": 890, "x": 4.2},
                {"label": "C008", "value": 520, "x": 3.5},
                {"label": "C009", "value": 1120, "x": 4.7},
                {"label": "C010", "value": 380, "x": 2.9},
                {"label": "C011", "value": 1340, "x": 4.6},
                {"label": "C012", "value": 750, "x": 3.8},
                {"label": "C013", "value": 920, "x": 4.1},
                {"label": "C014", "value": 480, "x": 3.3},
                {"label": "C015", "value": 1050, "x": 4.4},
                {"label": "C016", "value": 810, "x": 3.9},
                {"label": "C017", "value": 970, "x": 4.3},
                {"label": "C018", "value": 590, "x": 3.6},
                {"label": "C019", "value": 1420, "x": 4.8},
                {"label": "C020", "value": 410, "x": 3.1}
            ],
            "chart_preference": "scatter_plot",
            "theme": {
                "primary": "#06B6D4",
                "secondary": "#F59E0B",
                "style": "modern"
            },
            "enhance_labels": True
        }
    },
    {
        "name": "Heatmap - Weekly Activity Pattern",
        "request": {
            "content": "Show website traffic patterns across days of the week and hours",
            "title": "Weekly Website Traffic Heatmap",
            "data": [
                {"label": "Mon-00:00", "value": 120}, {"label": "Mon-03:00", "value": 85},
                {"label": "Mon-06:00", "value": 95}, {"label": "Mon-09:00", "value": 450},
                {"label": "Mon-12:00", "value": 680}, {"label": "Mon-15:00", "value": 720},
                {"label": "Mon-18:00", "value": 580}, {"label": "Mon-21:00", "value": 320},
                {"label": "Tue-00:00", "value": 115}, {"label": "Tue-03:00", "value": 82},
                {"label": "Tue-06:00", "value": 92}, {"label": "Tue-09:00", "value": 480},
                {"label": "Tue-12:00", "value": 690}, {"label": "Tue-15:00", "value": 710},
                {"label": "Tue-18:00", "value": 590}, {"label": "Tue-21:00", "value": 310},
                {"label": "Wed-00:00", "value": 125}, {"label": "Wed-03:00", "value": 88},
                {"label": "Wed-06:00", "value": 98}, {"label": "Wed-09:00", "value": 470},
                {"label": "Wed-12:00", "value": 700}, {"label": "Wed-15:00", "value": 730},
                {"label": "Wed-18:00", "value": 600}, {"label": "Wed-21:00", "value": 330},
                {"label": "Thu-00:00", "value": 118}, {"label": "Thu-03:00", "value": 86},
                {"label": "Thu-06:00", "value": 94}, {"label": "Thu-09:00", "value": 460},
                {"label": "Thu-12:00", "value": 685}, {"label": "Thu-15:00", "value": 715},
                {"label": "Thu-18:00", "value": 585}, {"label": "Thu-21:00", "value": 325},
                {"label": "Fri-00:00", "value": 130}, {"label": "Fri-03:00", "value": 90},
                {"label": "Fri-06:00", "value": 100}, {"label": "Fri-09:00", "value": 490},
                {"label": "Fri-12:00", "value": 710}, {"label": "Fri-15:00", "value": 740},
                {"label": "Fri-18:00", "value": 610}, {"label": "Fri-21:00", "value": 340},
                {"label": "Sat-00:00", "value": 180}, {"label": "Sat-03:00", "value": 120},
                {"label": "Sat-06:00", "value": 140}, {"label": "Sat-09:00", "value": 380},
                {"label": "Sat-12:00", "value": 520}, {"label": "Sat-15:00", "value": 480},
                {"label": "Sat-18:00", "value": 450}, {"label": "Sat-21:00", "value": 280},
                {"label": "Sun-00:00", "value": 190}, {"label": "Sun-03:00", "value": 130},
                {"label": "Sun-06:00", "value": 150}, {"label": "Sun-09:00", "value": 360},
                {"label": "Sun-12:00", "value": 510}, {"label": "Sun-15:00", "value": 470},
                {"label": "Sun-18:00", "value": 440}, {"label": "Sun-21:00", "value": 270}
            ],
            "chart_preference": "heatmap",
            "theme": {
                "primary": "#DC2626",
                "secondary": "#059669",
                "style": "modern"
            },
            "enhance_labels": True
        }
    }
]


async def test_single_chart(session_id: str, user_id: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test a single chart request
    
    Args:
        session_id: Session UUID
        user_id: User identifier
        test_case: Test case configuration
    
    Returns:
        Test result dictionary
    """
    uri = f"{WS_URL}?session_id={session_id}&user_id={user_id}"
    
    print_test(test_case["name"])
    
    result = {
        "test_name": test_case["name"],
        "success": False,
        "error": None,
        "response": None,
        "duration": 0
    }
    
    try:
        # Connect to WebSocket
        print_info(f"Connecting to: {uri}")
        
        # Create SSL context for secure connection
        ssl_context = None
        if uri.startswith("wss://"):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            # Wait for connection acknowledgment
            ack = await asyncio.wait_for(websocket.recv(), timeout=5)
            ack_data = json.loads(ack)
            
            if ack_data.get("type") == "connection_ack":
                print_success("Connection acknowledged")
            
            # Prepare request message
            message = {
                "message_id": f"msg_{uuid.uuid4()}",
                "correlation_id": f"test_{uuid.uuid4()}",
                "session_id": session_id,
                "type": "analytics_request",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "payload": test_case["request"]
            }
            
            # Send request
            print_info(f"Sending {test_case['request'].get('chart_preference', 'auto')} request...")
            start_time = datetime.now()
            await websocket.send(json.dumps(message))
            
            # Collect all responses
            responses = []
            final_response = None
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=TEST_TIMEOUT)
                    response_data = json.loads(response)
                    responses.append(response_data)
                    
                    msg_type = response_data.get("type")
                    
                    if msg_type == "status":
                        status = response_data.get("status", {}).get("state")
                        print_info(f"Status: {status}")
                    
                    elif msg_type == "analytics_response":
                        final_response = response_data
                        duration = (datetime.now() - start_time).total_seconds()
                        print_success(f"Received analytics response in {duration:.2f}s")
                        break
                    
                    elif msg_type == "error":
                        error_msg = response_data.get("payload", {}).get("message", "Unknown error")
                        print_error(f"Error: {error_msg}")
                        result["error"] = error_msg
                        break
                        
                except asyncio.TimeoutError:
                    print_error("Timeout waiting for response")
                    result["error"] = "Timeout"
                    break
            
            # Process final response
            if final_response:
                payload = final_response.get("payload", {})
                
                # Validate response structure
                has_chart = bool(payload.get("chart"))
                has_metadata = bool(payload.get("metadata"))
                has_data = bool(payload.get("data"))
                
                if has_chart:
                    chart_size = len(payload["chart"]) // 1024
                    print_success(f"Chart received: {chart_size}KB base64 image")
                
                if has_metadata:
                    metadata = payload["metadata"]
                    print_success(f"Metadata: {metadata.get('title', 'No title')}")
                
                if has_data:
                    insights = payload.get("metadata", {}).get("insights", [])
                    if insights:
                        print_success(f"Insights: {len(insights)} insights generated")
                
                result["success"] = has_chart and has_metadata
                result["response"] = payload
                result["duration"] = duration
            
    except websockets.exceptions.WebSocketException as e:
        print_error(f"WebSocket error: {e}")
        result["error"] = str(e)
    
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        result["error"] = str(e)
    
    return result


def generate_html_report(results: List[Dict[str, Any]]) -> str:
    """
    Generate HTML report with all test results
    
    Args:
        results: List of test results
    
    Returns:
        HTML content as string
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Railway Deployment Test Results</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.2em;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .summary-card .label {
            color: #666;
            margin-top: 5px;
        }
        .test-results {
            display: grid;
            gap: 30px;
        }
        .test-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        .test-title {
            font-size: 1.5em;
            color: #333;
        }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.85em;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .metadata {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .metadata h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .metadata-item {
            background: white;
            padding: 10px 15px;
            border-radius: 5px;
        }
        .metadata-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .metadata-value {
            color: #333;
            font-weight: 500;
        }
        .insights {
            background: #e7f3ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }
        .insights h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .insight-item {
            margin: 10px 0;
            padding-left: 20px;
            position: relative;
        }
        .insight-item:before {
            content: "→";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Railway Deployment Test Results</h1>
            <div class="subtitle">Analytics Microservice V2 - WebSocket API Testing</div>
            <div class="subtitle" style="margin-top: 10px; font-size: 1em; color: #999;">
                Endpoint: """ + WS_URL + """
            </div>
            
            <div class="summary">
                <div class="summary-card">
                    <div class="value">""" + str(len(results)) + """</div>
                    <div class="label">Total Tests</div>
                </div>
                <div class="summary-card">
                    <div class="value">""" + str(sum(1 for r in results if r["success"])) + """</div>
                    <div class="label">Successful</div>
                </div>
                <div class="summary-card">
                    <div class="value">""" + str(sum(1 for r in results if not r["success"])) + """</div>
                    <div class="label">Failed</div>
                </div>
                <div class="summary-card">
                    <div class="value">""" + f"{sum(r.get('duration', 0) for r in results):.1f}s" + """</div>
                    <div class="label">Total Duration</div>
                </div>
            </div>
        </div>
        
        <div class="test-results">
    """
    
    for i, result in enumerate(results, 1):
        status_class = "status-success" if result["success"] else "status-error"
        status_text = "SUCCESS" if result["success"] else "ERROR"
        
        html += f"""
            <div class="test-card">
                <div class="test-header">
                    <div class="test-title">Test #{i}: {result['test_name']}</div>
                    <div class="status-badge {status_class}">{status_text}</div>
                </div>
        """
        
        if result["success"] and result.get("response"):
            response = result["response"]
            
            # Display chart
            if response.get("chart"):
                html += f"""
                <div class="chart-container">
                    <img src="data:image/png;base64,{response['chart']}" alt="{result['test_name']}">
                </div>
                """
            
            # Display metadata
            if response.get("metadata"):
                metadata = response["metadata"]
                html += """
                <div class="metadata">
                    <h3>📊 Chart Metadata</h3>
                    <div class="metadata-grid">
                """
                
                for key, value in metadata.items():
                    if key not in ["chart", "insights"]:
                        html += f"""
                        <div class="metadata-item">
                            <div class="metadata-label">{key.replace('_', ' ').title()}</div>
                            <div class="metadata-value">{value}</div>
                        </div>
                        """
                
                html += """
                    </div>
                </div>
                """
            
            # Display insights
            if response.get("insights"):
                html += """
                <div class="insights">
                    <h3>💡 Insights</h3>
                """
                for insight in response["insights"]:
                    html += f'<div class="insight-item">{insight}</div>'
                html += "</div>"
        
        elif result.get("error"):
            html += f"""
                <div class="error-message">
                    <strong>Error:</strong> {result['error']}
                </div>
            """
        
        # Add duration
        if result.get("duration"):
            html += f"""
                <div style="text-align: right; color: #999; margin-top: 10px;">
                    Duration: {result['duration']:.2f} seconds
                </div>
            """
        
        html += "</div>"
    
    html += f"""
        </div>
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
    """
    
    return html


async def main():
    """Main test execution"""
    print_header("Analytics Microservice V2 - Railway Deployment Test")
    print_info(f"Testing endpoint: {WS_URL}")
    print_info(f"Number of tests: {len(TEST_CASES)}")
    
    # Generate session and user IDs
    session_id = str(uuid.uuid4())
    user_id = "railway_test_suite"
    
    print_info(f"Session ID: {session_id}")
    print_info(f"User ID: {user_id}")
    
    # Run all tests
    results = []
    
    for test_case in TEST_CASES:
        result = await test_single_chart(session_id, user_id, test_case)
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    print_header("Test Summary")
    successful = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    total_duration = sum(r.get("duration", 0) for r in results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
    print(f"  Total Tests: {len(results)}")
    print(f"  {Colors.GREEN}Successful: {successful}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"  Total Duration: {total_duration:.2f} seconds")
    print(f"  Average Duration: {total_duration/len(results):.2f} seconds")
    
    # Save results
    if SAVE_RESULTS:
        # Save JSON results
        json_filename = "railway_test_results.json"
        with open(json_filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print_success(f"JSON results saved to {json_filename}")
        
        # Save HTML report
        html_filename = "railway_test_results.html"
        html_content = generate_html_report(results)
        with open(html_filename, "w") as f:
            f.write(html_content)
        print_success(f"HTML report saved to {html_filename}")
        print_info(f"Open {html_filename} in a browser to view the charts")
    
    # Return exit code based on results
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)