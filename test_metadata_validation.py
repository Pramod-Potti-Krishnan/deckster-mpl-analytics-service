#!/usr/bin/env python3
"""
Test Enhanced Metadata and Table Data
======================================

Verify that the WebSocket response includes:
1. Complete metadata (title, axis labels, axis types)
2. Table-ready data format
3. All necessary information for client display

Author: Analytics Agent System V2
Date: 2024
"""

import asyncio
import json
import websockets
from datetime import datetime
import uuid
import base64
from typing import Dict, Any, List


async def test_single_chart(chart_type: str, content: str, title: str) -> Dict[str, Any]:
    """Test a single chart and return the response."""
    uri = "ws://localhost:8000/ws"
    session_id = str(uuid.uuid4())
    
    try:
        async with websockets.connect(f"{uri}?session_id={session_id}&user_id=test_metadata") as websocket:
            # Wait for connection ack
            ack = await websocket.recv()
            
            # Send request
            request = {
                "message_id": f"msg_{uuid.uuid4()}",
                "correlation_id": f"corr_{uuid.uuid4()}",
                "session_id": session_id,
                "type": "analytics_request",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "content": content,
                    "title": title,
                    "chart_preference": chart_type,
                    "use_synthetic_data": True,
                    "enhance_labels": True
                }
            }
            
            await websocket.send(json.dumps(request))
            
            # Collect responses
            analytics_response = None
            
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(response)
                    
                    if data['type'] == 'analytics_response':
                        analytics_response = data['payload']
                        break
                    elif data['type'] == 'error':
                        return {"error": data['payload'].get('message')}
                        
            except asyncio.TimeoutError:
                pass
            
            return analytics_response
                    
    except Exception as e:
        return {"error": str(e)}


def verify_metadata(response: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
    """Verify that all metadata fields are present and populated."""
    results = {
        "chart_type": chart_type,
        "success": response.get("success", False),
        "has_chart": False,
        "has_metadata": False,
        "has_table_data": False,
        "metadata_complete": False,
        "table_ready": False,
        "issues": []
    }
    
    if not results["success"]:
        results["issues"].append(f"Chart generation failed: {response.get('error', 'Unknown error')}")
        return results
    
    # Check chart data
    if response.get("chart"):
        results["has_chart"] = True
        # Verify it's valid base64
        try:
            chart_bytes = base64.b64decode(response["chart"])
            if chart_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                results["chart_valid"] = True
            else:
                results["issues"].append("Chart is not a valid PNG")
        except:
            results["issues"].append("Chart is not valid base64")
    else:
        results["issues"].append("No chart data in response")
    
    # Check metadata
    if "metadata" in response:
        results["has_metadata"] = True
        metadata = response["metadata"]
        
        # Required metadata fields
        required_fields = [
            "chart_type", "title", "x_axis_label", "y_axis_label",
            "x_axis_type", "y_axis_type", "generation_time_ms",
            "data_points_count"
        ]
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in metadata:
                missing_fields.append(field)
            elif metadata[field] == "" or metadata[field] is None:
                empty_fields.append(field)
        
        if not missing_fields and not empty_fields:
            results["metadata_complete"] = True
        else:
            if missing_fields:
                results["issues"].append(f"Missing metadata fields: {missing_fields}")
            if empty_fields:
                results["issues"].append(f"Empty metadata fields: {empty_fields}")
        
        # Store metadata details
        results["metadata_details"] = {
            "title": metadata.get("title", ""),
            "x_axis_label": metadata.get("x_axis_label", ""),
            "y_axis_label": metadata.get("y_axis_label", ""),
            "x_axis_type": metadata.get("x_axis_type", ""),
            "y_axis_type": metadata.get("y_axis_type", ""),
            "data_points": metadata.get("data_points_count", 0)
        }
    else:
        results["issues"].append("No metadata in response")
    
    # Check table data
    if "data" in response:
        data = response["data"]
        
        # Check for table-ready format
        if "table_data" in data and "table_columns" in data:
            results["has_table_data"] = True
            
            table_data = data["table_data"]
            table_columns = data["table_columns"]
            
            if isinstance(table_data, list) and isinstance(table_columns, list):
                if len(table_data) > 0 and len(table_columns) > 0:
                    # Verify table structure
                    first_row = table_data[0]
                    if all(col in first_row for col in table_columns):
                        results["table_ready"] = True
                    else:
                        results["issues"].append("Table columns don't match table data keys")
                else:
                    results["issues"].append("Table data or columns are empty")
            else:
                results["issues"].append("Table data format is incorrect")
        else:
            results["issues"].append("No table_data or table_columns in response")
        
        # Store table details
        if results["has_table_data"]:
            results["table_details"] = {
                "columns": data.get("table_columns", []),
                "row_count": len(data.get("table_data", [])),
                "sample_row": data.get("table_data", [{}])[0] if data.get("table_data") else {}
            }
    else:
        results["issues"].append("No data section in response")
    
    return results


async def test_all_charts():
    """Test multiple chart types for metadata completeness."""
    
    test_cases = [
        ("bar_chart_vertical", "Show Q1 2024 sales by product category", "Q1 2024 Sales"),
        ("line_chart", "Display monthly revenue trend for 2024", "Revenue Trend"),
        ("pie_chart", "Market share distribution across segments", "Market Share"),
        ("scatter_plot", "Correlation between price and demand", "Price vs Demand"),
        ("histogram", "Distribution of customer satisfaction scores", "Satisfaction Distribution"),
        ("grouped_bar_chart", "Compare sales across regions and quarters", "Regional Sales Comparison"),
    ]
    
    print("\n" + "="*80)
    print("ENHANCED METADATA AND TABLE DATA TEST")
    print("="*80 + "\n")
    
    all_results = []
    
    for chart_type, content, title in test_cases:
        print(f"\nTesting {chart_type}...")
        print(f"  Content: {content}")
        print(f"  Title: {title}")
        
        response = await test_single_chart(chart_type, content, title)
        results = verify_metadata(response, chart_type)
        all_results.append(results)
        
        # Print results
        print(f"\n  Results:")
        print(f"    ✅ Success: {results['success']}")
        print(f"    {'✅' if results['has_chart'] else '❌'} Has chart data")
        print(f"    {'✅' if results['metadata_complete'] else '❌'} Metadata complete")
        print(f"    {'✅' if results['table_ready'] else '❌'} Table data ready")
        
        if results.get('metadata_details'):
            print(f"\n  Metadata:")
            for key, value in results['metadata_details'].items():
                print(f"    {key}: {value}")
        
        if results.get('table_details'):
            print(f"\n  Table Data:")
            print(f"    Columns: {results['table_details']['columns']}")
            print(f"    Rows: {results['table_details']['row_count']}")
            if results['table_details']['sample_row']:
                print(f"    Sample: {json.dumps(results['table_details']['sample_row'], indent=6)}")
        
        if results['issues']:
            print(f"\n  Issues:")
            for issue in results['issues']:
                print(f"    ⚠️  {issue}")
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    successful = sum(1 for r in all_results if r['success'])
    metadata_complete = sum(1 for r in all_results if r['metadata_complete'])
    table_ready = sum(1 for r in all_results if r['table_ready'])
    
    print(f"Charts tested: {len(all_results)}")
    print(f"Successful: {successful}/{len(all_results)}")
    print(f"Metadata complete: {metadata_complete}/{len(all_results)}")
    print(f"Table data ready: {table_ready}/{len(all_results)}")
    
    if metadata_complete == len(all_results) and table_ready == len(all_results):
        print("\n✅ ALL TESTS PASSED! Metadata and table data enhancements working correctly.")
    else:
        print("\n⚠️  Some tests failed. Review the issues above.")
    
    # Generate HTML report
    generate_html_report(all_results)


def generate_html_report(results: List[Dict[str, Any]]):
    """Generate an HTML report showing the enhanced metadata."""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Metadata Test Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        .chart-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .chart-type {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .status {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
        }
        .status.success {
            background: #10b981;
            color: white;
        }
        .status.failed {
            background: #ef4444;
            color: white;
        }
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metadata-item {
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
        }
        .metadata-label {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 5px;
        }
        .metadata-value {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
        }
        .table-preview {
            margin-top: 20px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        .issues {
            margin-top: 15px;
            padding: 10px;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 5px;
            color: #991b1b;
        }
        .check-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .check-icon {
            margin-right: 8px;
        }
        .summary {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-top: 30px;
            text-align: center;
        }
        .summary h2 {
            color: #333;
            margin-bottom: 20px;
        }
        .summary-stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 14px;
            color: #6b7280;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Enhanced Metadata & Table Data Test Report</h1>
"""
    
    # Add each chart result
    for result in results:
        status_class = "success" if result["success"] else "failed"
        status_text = "SUCCESS" if result["success"] else "FAILED"
        
        html += f"""
        <div class="chart-card">
            <div class="chart-header">
                <div class="chart-type">{result['chart_type']}</div>
                <div class="status {status_class}">{status_text}</div>
            </div>
            
            <div class="check-item">
                <span class="check-icon">{'✅' if result['has_chart'] else '❌'}</span>
                Chart Data Present
            </div>
            <div class="check-item">
                <span class="check-icon">{'✅' if result['metadata_complete'] else '❌'}</span>
                Metadata Complete
            </div>
            <div class="check-item">
                <span class="check-icon">{'✅' if result['table_ready'] else '❌'}</span>
                Table Data Ready
            </div>
"""
        
        # Add metadata details
        if result.get('metadata_details'):
            html += '<div class="metadata-grid">'
            for key, value in result['metadata_details'].items():
                label = key.replace('_', ' ').title()
                html += f"""
                <div class="metadata-item">
                    <div class="metadata-label">{label}</div>
                    <div class="metadata-value">{value}</div>
                </div>
"""
            html += '</div>'
        
        # Add table preview
        if result.get('table_details') and result['table_details']['columns']:
            html += '<div class="table-preview">'
            html += '<h4>Table Data Preview</h4>'
            html += '<table>'
            html += '<thead><tr>'
            for col in result['table_details']['columns']:
                html += f'<th>{col}</th>'
            html += '</tr></thead>'
            html += '<tbody><tr>'
            sample = result['table_details'].get('sample_row', {})
            for col in result['table_details']['columns']:
                value = sample.get(col, '')
                html += f'<td>{value}</td>'
            html += '</tr></tbody>'
            html += '</table>'
            html += f'<p style="color: #6b7280; font-size: 12px; margin-top: 5px;">Total rows: {result["table_details"]["row_count"]}</p>'
            html += '</div>'
        
        # Add issues if any
        if result.get('issues'):
            html += '<div class="issues">'
            html += '<strong>Issues:</strong><ul style="margin: 5px 0; padding-left: 20px;">'
            for issue in result['issues']:
                html += f'<li>{issue}</li>'
            html += '</ul></div>'
        
        html += '</div>'
    
    # Add summary
    successful = sum(1 for r in results if r['success'])
    metadata_complete = sum(1 for r in results if r['metadata_complete'])
    table_ready = sum(1 for r in results if r['table_ready'])
    
    html += f"""
        <div class="summary">
            <h2>Test Summary</h2>
            <div class="summary-stats">
                <div class="stat">
                    <div class="stat-value">{successful}/{len(results)}</div>
                    <div class="stat-label">Successful Charts</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{metadata_complete}/{len(results)}</div>
                    <div class="stat-label">Complete Metadata</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{table_ready}/{len(results)}</div>
                    <div class="stat-label">Table Ready</div>
                </div>
            </div>
"""
    
    if metadata_complete == len(results) and table_ready == len(results):
        html += '<p style="color: #10b981; font-size: 18px; font-weight: bold;">✅ All enhancements working correctly!</p>'
    else:
        html += '<p style="color: #ef4444; font-size: 18px; font-weight: bold;">⚠️ Some enhancements need attention</p>'
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    # Save the report
    with open("enhanced_metadata_report.html", "w") as f:
        f.write(html)
    
    print(f"\n📄 HTML report saved to: enhanced_metadata_report.html")


if __name__ == "__main__":
    print("Starting Enhanced Metadata Test...")
    print("Make sure the WebSocket server is running on localhost:8000")
    print("-" * 80)
    
    asyncio.run(test_all_charts())