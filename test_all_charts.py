#!/usr/bin/env python3
"""
Comprehensive Test Suite for Analytics Microservice V2
Tests all 23 chart types via WebSocket with feedback collection
"""

import asyncio
import json
import uuid
import base64
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import websockets
import aiohttp
from pathlib import Path

# Test configuration
TEST_HOST = "localhost"
TEST_PORT = 8000
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
WS_URL = f"ws://{TEST_HOST}:{TEST_PORT}/ws"

# Create test results directory
TEST_DIR = Path("test_results")
TEST_DIR.mkdir(exist_ok=True)


class AnalyticsTestClient:
    """WebSocket client for testing analytics generation"""
    
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id = str(uuid.uuid4())
        self.results = []
        self.pending_requests = {}
        self.message_log = []
        
    async def connect(self):
        """Establish WebSocket connection"""
        uri = f"{WS_URL}?session_id={self.session_id}&user_id=test_client"
        self.ws = await websockets.connect(uri)
        
        # Wait for connection acknowledgment
        ack = await self.ws.recv()
        ack_data = json.loads(ack)
        self.message_log.append(("received", ack_data))
        
        if ack_data.get("type") == "control" and ack_data.get("subtype") == "connection_ack":
            print("✅ WebSocket connected successfully")
            return True
        return False
    
    async def generate_chart(
        self,
        content: str,
        chart_type: Optional[str] = None,
        data: Optional[List[Dict]] = None,
        theme: Optional[Dict] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a chart via WebSocket"""
        
        request_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # Build request
        request = {
            "message_id": message_id,
            "correlation_id": request_id,
            "request_id": request_id,
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "analytics_request",
            "payload": {
                "content": content,
                "use_synthetic_data": data is None,
                "enhance_labels": True
            }
        }
        
        if chart_type:
            request["payload"]["chart_preference"] = chart_type
        if data:
            request["payload"]["data"] = data
        if theme:
            request["payload"]["theme"] = theme
        if title:
            request["payload"]["title"] = title
        
        # Send request
        start_time = time.time()
        await self.ws.send(json.dumps(request))
        self.message_log.append(("sent", request))
        
        # Collect responses
        responses = []
        final_response = None
        
        while True:
            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
                response_data = json.loads(response)
                self.message_log.append(("received", response_data))
                responses.append(response_data)
                
                # Check if this is the final response
                if response_data.get("type") == "analytics_response":
                    final_response = response_data
                    break
                elif response_data.get("type") == "error":
                    final_response = response_data
                    break
                    
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout waiting for response to {request_id}")
                break
        
        # Calculate metrics
        generation_time = (time.time() - start_time) * 1000  # ms
        
        if final_response:
            # Save chart image if successful
            chart_path = None
            if (final_response.get("type") == "analytics_response" and 
                final_response.get("payload", {}).get("success")):
                
                chart_base64 = final_response["payload"].get("chart")
                if chart_base64:
                    # Save chart image
                    chart_filename = f"{chart_type or 'chart'}_{request_id[:8]}.png"
                    chart_path = TEST_DIR / chart_filename
                    
                    # Decode and save
                    if chart_base64.startswith("data:image"):
                        chart_base64 = chart_base64.split(",")[1]
                    
                    with open(chart_path, "wb") as f:
                        f.write(base64.b64decode(chart_base64))
            
            return {
                "request_id": request_id,
                "success": final_response.get("payload", {}).get("success", False),
                "chart_type": chart_type,
                "content": content,
                "generation_time_ms": generation_time,
                "chart_path": str(chart_path) if chart_path else None,
                "response": final_response,
                "all_responses": responses,
                "error": final_response.get("payload", {}).get("error") if final_response.get("type") == "error" else None
            }
        
        return {
            "request_id": request_id,
            "success": False,
            "chart_type": chart_type,
            "content": content,
            "generation_time_ms": generation_time,
            "error": "No response received",
            "all_responses": responses
        }
    
    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()


class ComprehensiveTestSuite:
    """Comprehensive test suite for all chart types"""
    
    def __init__(self):
        self.client = AnalyticsTestClient()
        self.test_results = {
            "test_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {},
            "chart_tests": [],
            "performance_metrics": {},
            "errors": []
        }
    
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define test scenarios for all 23 chart types"""
        
        scenarios = [
            # Line and Trend Charts
            {
                "chart_type": "line_chart",
                "content": "Show monthly revenue growth from January to December 2024",
                "title": "Monthly Revenue Trend",
                "category": "Line and Trend"
            },
            {
                "chart_type": "step_chart",
                "content": "Display quarterly employee count changes for the year",
                "title": "Employee Growth Steps",
                "category": "Line and Trend"
            },
            {
                "chart_type": "area_chart",
                "content": "Visualize website traffic volume over the past 12 months",
                "title": "Traffic Volume",
                "category": "Line and Trend"
            },
            {
                "chart_type": "stacked_area_chart",
                "content": "Show revenue breakdown by product categories over quarters",
                "title": "Revenue by Category",
                "category": "Line and Trend"
            },
            
            # Bar Charts
            {
                "chart_type": "bar_chart_vertical",
                "content": "Compare sales performance across 8 different regions",
                "title": "Regional Sales",
                "category": "Bar Charts"
            },
            {
                "chart_type": "bar_chart_horizontal",
                "content": "Rank top 10 products by customer satisfaction score",
                "title": "Product Satisfaction",
                "category": "Bar Charts"
            },
            {
                "chart_type": "grouped_bar_chart",
                "content": "Compare Q1 vs Q2 performance across 5 departments",
                "title": "Department Comparison",
                "category": "Bar Charts"
            },
            {
                "chart_type": "stacked_bar_chart",
                "content": "Show expense breakdown by category for each month",
                "title": "Monthly Expenses",
                "category": "Bar Charts"
            },
            
            # Distribution Charts
            {
                "chart_type": "histogram",
                "content": "Show distribution of customer ages in our database",
                "title": "Age Distribution",
                "category": "Distribution"
            },
            {
                "chart_type": "box_plot",
                "content": "Display salary ranges across different job levels",
                "title": "Salary Ranges",
                "category": "Distribution"
            },
            {
                "chart_type": "violin_plot",
                "content": "Visualize response time distribution for different servers",
                "title": "Server Response Times",
                "category": "Distribution"
            },
            
            # Correlation Charts
            {
                "chart_type": "scatter_plot",
                "content": "Show correlation between marketing spend and sales revenue",
                "title": "Marketing vs Sales",
                "category": "Correlation"
            },
            {
                "chart_type": "bubble_chart",
                "content": "Display products by price, units sold, and profit margin",
                "title": "Product Analysis",
                "category": "Correlation"
            },
            {
                "chart_type": "hexbin",
                "content": "Visualize density of customer locations on a map grid",
                "title": "Customer Density",
                "category": "Correlation"
            },
            
            # Composition Charts
            {
                "chart_type": "pie_chart",
                "content": "Show market share distribution among top 5 competitors",
                "title": "Market Share",
                "category": "Composition"
            },
            {
                "chart_type": "waterfall",
                "content": "Display profit breakdown from revenue to net income",
                "title": "Profit Waterfall",
                "category": "Composition"
            },
            {
                "chart_type": "funnel",
                "content": "Show conversion rates through sales pipeline stages",
                "title": "Sales Funnel",
                "category": "Composition"
            },
            
            # Comparison Charts
            {
                "chart_type": "radar_chart",
                "content": "Compare skills assessment across 6 competency areas",
                "title": "Skills Assessment",
                "category": "Comparison"
            },
            {
                "chart_type": "heatmap",
                "content": "Show correlation matrix between different product features",
                "title": "Feature Correlation",
                "category": "Comparison"
            },
            
            # Statistical Charts
            {
                "chart_type": "error_bar_chart",
                "content": "Display experimental results with confidence intervals",
                "title": "Experiment Results",
                "category": "Statistical"
            },
            {
                "chart_type": "control_chart",
                "content": "Monitor manufacturing quality metrics over time",
                "title": "Quality Control",
                "category": "Statistical"
            },
            {
                "chart_type": "pareto",
                "content": "Analyze top causes of customer complaints",
                "title": "Complaint Analysis",
                "category": "Statistical"
            },
            
            # Project Charts
            {
                "chart_type": "gantt",
                "content": "Show project timeline with 5 major milestones and dependencies",
                "title": "Project Timeline",
                "category": "Project"
            }
        ]
        
        # Add theme variations for some charts
        themes = [
            {"primary": "#3B82F6", "secondary": "#10B981", "tertiary": "#F59E0B"},
            {"primary": "#EF4444", "secondary": "#8B5CF6", "tertiary": "#14B8A6"},
            {"primary": "#6366F1", "secondary": "#EC4899", "tertiary": "#F97316"}
        ]
        
        # Add a few scenarios with custom data
        scenarios.append({
            "chart_type": "bar_chart_vertical",
            "content": "Visualize quarterly results",
            "title": "Custom Data Test",
            "category": "Bar Charts",
            "data": [
                {"label": "Q1", "value": 45000},
                {"label": "Q2", "value": 52000},
                {"label": "Q3", "value": 48000},
                {"label": "Q4", "value": 61000}
            ],
            "theme": themes[0]
        })
        
        return scenarios
    
    async def run_health_checks(self) -> bool:
        """Check if the service is healthy"""
        print("\n🏥 Running Health Checks...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Check health endpoint
                async with session.get(f"{BASE_URL}/health") as resp:
                    if resp.status == 200:
                        health_data = await resp.json()
                        print(f"✅ Service is {health_data['status']}")
                        print(f"   Components: {json.dumps(health_data.get('components', {}), indent=2)}")
                        return True
                    else:
                        print(f"❌ Health check failed with status {resp.status}")
                        return False
                        
            except Exception as e:
                print(f"❌ Failed to connect to service: {e}")
                return False
    
    async def run_tests(self):
        """Run all test scenarios"""
        print("\n🚀 Starting Comprehensive Analytics Tests")
        print("=" * 60)
        
        # Health check
        if not await self.run_health_checks():
            print("❌ Service health check failed. Please start the service first.")
            return
        
        # Connect WebSocket
        print("\n📡 Connecting WebSocket...")
        try:
            await self.client.connect()
        except Exception as e:
            print(f"❌ Failed to connect WebSocket: {e}")
            return
        
        # Get test scenarios
        scenarios = self.get_test_scenarios()
        total_tests = len(scenarios)
        
        print(f"\n📊 Testing {total_tests} chart scenarios...")
        print("=" * 60)
        
        # Run each test
        passed = 0
        failed = 0
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{total_tests}] Testing {scenario['chart_type']}...")
            print(f"   Content: {scenario['content'][:50]}...")
            
            try:
                # Run test
                result = await self.client.generate_chart(
                    content=scenario["content"],
                    chart_type=scenario["chart_type"],
                    title=scenario.get("title"),
                    data=scenario.get("data"),
                    theme=scenario.get("theme")
                )
                
                # Store result
                test_result = {
                    **scenario,
                    **result,
                    "test_number": i
                }
                self.test_results["chart_tests"].append(test_result)
                
                # Update counters
                if result["success"]:
                    passed += 1
                    print(f"   ✅ Success! Generated in {result['generation_time_ms']:.0f}ms")
                    if result.get("chart_path"):
                        print(f"   📁 Saved to: {result['chart_path']}")
                else:
                    failed += 1
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                failed += 1
                print(f"   ❌ Exception: {e}")
                self.test_results["errors"].append({
                    "chart_type": scenario["chart_type"],
                    "error": str(e)
                })
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Close connection
        await self.client.close()
        
        # Calculate summary
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "total_time": sum(t.get("generation_time_ms", 0) for t in self.test_results["chart_tests"]),
            "average_time": sum(t.get("generation_time_ms", 0) for t in self.test_results["chart_tests"]) / total_tests if total_tests > 0 else 0
        }
        
        # Performance metrics by chart type
        chart_metrics = {}
        for test in self.test_results["chart_tests"]:
            chart_type = test["chart_type"]
            if chart_type not in chart_metrics:
                chart_metrics[chart_type] = {
                    "count": 0,
                    "success": 0,
                    "total_time": 0,
                    "times": []
                }
            
            chart_metrics[chart_type]["count"] += 1
            if test["success"]:
                chart_metrics[chart_type]["success"] += 1
            chart_metrics[chart_type]["total_time"] += test.get("generation_time_ms", 0)
            chart_metrics[chart_type]["times"].append(test.get("generation_time_ms", 0))
        
        # Calculate averages
        for chart_type, metrics in chart_metrics.items():
            metrics["success_rate"] = (metrics["success"] / metrics["count"] * 100) if metrics["count"] > 0 else 0
            metrics["average_time"] = metrics["total_time"] / metrics["count"] if metrics["count"] > 0 else 0
            del metrics["times"]  # Remove raw times for cleaner output
        
        self.test_results["performance_metrics"] = chart_metrics
        
        # Print summary
        print("\n" + "=" * 60)
        print("📈 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
        print(f"Average Generation Time: {self.test_results['summary']['average_time']:.0f}ms")
        print(f"Total Test Time: {self.test_results['summary']['total_time']/1000:.1f}s")
        
        # Save results to JSON
        results_file = TEST_DIR / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {results_file}")
        
        return self.test_results


async def main():
    """Main test execution"""
    suite = ComprehensiveTestSuite()
    results = await suite.run_tests()
    
    if results:
        print("\n✅ Test suite completed!")
        print(f"📊 Generated {len([t for t in results['chart_tests'] if t['success']])} charts successfully")
        print(f"📁 Check the test_results/ directory for generated charts")
        print("\n🌐 Generating HTML report...")
        
        # Generate HTML report
        from test_report_generator import generate_html_report
        report_path = generate_html_report(results)
        print(f"📄 HTML report generated: {report_path}")
        
        # Open in browser
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(report_path)}")
    else:
        print("\n❌ Test suite failed to complete")


if __name__ == "__main__":
    asyncio.run(main())