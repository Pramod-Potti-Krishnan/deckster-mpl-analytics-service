#!/usr/bin/env python3
"""
Test script to verify heatmap fix with various data formats
"""

import asyncio
import websockets
import json
import uuid
from datetime import datetime
import ssl

RAILWAY_URL = "wss://deckster-mpl-analytics-service-production.up.railway.app/ws"

async def test_heatmap():
    """Test heatmap with various data formats"""
    
    test_cases = [
        {
            "name": "Format 1: Label with dash separator",
            "data": [
                {"label": "Mon-09:00", "value": 450},
                {"label": "Mon-12:00", "value": 680},
                {"label": "Mon-15:00", "value": 720},
                {"label": "Tue-09:00", "value": 480},
                {"label": "Tue-12:00", "value": 690},
                {"label": "Tue-15:00", "value": 710},
                {"label": "Wed-09:00", "value": 470},
                {"label": "Wed-12:00", "value": 700},
                {"label": "Wed-15:00", "value": 730}
            ]
        },
        {
            "name": "Format 2: Separate day/hour fields",
            "data": [
                {"day": "Monday", "hour": "9AM", "traffic": 450},
                {"day": "Monday", "hour": "12PM", "traffic": 680},
                {"day": "Monday", "hour": "3PM", "traffic": 720},
                {"day": "Tuesday", "hour": "9AM", "traffic": 480},
                {"day": "Tuesday", "hour": "12PM", "traffic": 690},
                {"day": "Tuesday", "hour": "3PM", "traffic": 710}
            ]
        },
        {
            "name": "Format 3: Space-separated label",
            "data": [
                {"label": "Monday Morning", "value": 450},
                {"label": "Monday Afternoon", "value": 680},
                {"label": "Monday Evening", "value": 520},
                {"label": "Tuesday Morning", "value": 480},
                {"label": "Tuesday Afternoon", "value": 690},
                {"label": "Tuesday Evening", "value": 530}
            ]
        }
    ]
    
    session_id = str(uuid.uuid4())
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"{'='*60}")
        
        uri = f"{RAILWAY_URL}?session_id={session_id}&user_id=heatmap_test"
        
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Wait for connection ack
                ack = await asyncio.wait_for(websocket.recv(), timeout=5)
                ack_data = json.loads(ack)
                print(f"✅ Connected: {ack_data.get('type')}")
                
                # Send heatmap request
                message = {
                    "message_id": f"msg_{uuid.uuid4()}",
                    "correlation_id": f"test_{uuid.uuid4()}",
                    "session_id": session_id,
                    "type": "analytics_request",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "payload": {
                        "content": "Show activity heatmap",
                        "title": f"Heatmap Test - {test_case['name']}",
                        "data": test_case["data"],
                        "chart_preference": "heatmap",
                        "theme": {
                            "primary": "#DC2626",
                            "secondary": "#059669",
                            "style": "modern"
                        }
                    }
                }
                
                print(f"📊 Sending request with {len(test_case['data'])} data points...")
                await websocket.send(json.dumps(message))
                
                # Collect responses
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    response_data = json.loads(response)
                    msg_type = response_data.get("type")
                    
                    if msg_type == "status":
                        status = response_data.get("payload", {}).get("status")
                        print(f"⏳ Status: {status}")
                    
                    elif msg_type == "analytics_response":
                        payload = response_data.get("payload", {})
                        if payload.get("chart"):
                            print(f"✅ Chart received!")
                            metadata = payload.get("metadata", {})
                            print(f"   Title: {metadata.get('title')}")
                            print(f"   Data points: {metadata.get('data_points_count')}")
                            
                            # Check if we have actual data
                            data = payload.get("data", {})
                            if data:
                                stats = data.get("statistics", {})
                                print(f"   Value range: {stats.get('min')} to {stats.get('max')}")
                                print(f"   Average: {stats.get('mean')}")
                        break
                    
                    elif msg_type == "error":
                        error_msg = response_data.get("payload", {}).get("message")
                        print(f"❌ Error: {error_msg}")
                        break
                        
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("All heatmap format tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_heatmap())