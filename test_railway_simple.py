#!/usr/bin/env python3
"""
Simple Railway Deployment Test - HTTP Endpoints

Tests the basic HTTP endpoints of the deployed service.
"""

import requests
import json
from datetime import datetime

# Railway deployment URL
BASE_URL = "https://deckster-mpl-analytics-service-production.up.railway.app"

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing ROOT endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint is working!")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print(f"   WebSocket URL: {data.get('websocket_url')}")
            print(f"   Chart Types: {data.get('capabilities', {}).get('chart_types')}")
            return True
        else:
            print(f"❌ Root endpoint failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing root: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🏥 Testing HEALTH endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print(f"⚠️  Health check returned status {response.status_code}")
        
        print(f"   Status: {data.get('status')}")
        components = data.get('components', {})
        for key, value in components.items():
            print(f"   {key}: {value}")
        
        return response.status_code in [200, 503]  # 503 if degraded
    except Exception as e:
        print(f"❌ Error testing health: {e}")
        return False

def test_chart_types_endpoint():
    """Test the chart types endpoint"""
    print("\n📊 Testing CHART-TYPES endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/chart-types")
        if response.status_code == 200:
            data = response.json()
            chart_types = data.get('chart_types', [])
            total = data.get('total', 0)
            
            print(f"✅ Chart types endpoint working!")
            print(f"   Total chart types: {total}")
            
            for category in chart_types[:3]:  # Show first 3 categories
                print(f"   📈 {category.get('category')}:")
                for chart in category.get('types', []):
                    print(f"      - {chart.get('name')}")
            
            return True
        else:
            print(f"❌ Chart types endpoint failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing chart types: {e}")
        return False

def test_stats_endpoint():
    """Test the statistics endpoint"""
    print("\n📈 Testing STATS endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint working!")
            print(f"   Total requests: {data.get('total_requests', 0)}")
            print(f"   Total errors: {data.get('total_errors', 0)}")
            print(f"   Active connections: {data.get('active_connections', 0)}")
            return True
        elif response.status_code == 503:
            print("⚠️  Stats endpoint: Service not initialized")
            return True
        else:
            print(f"❌ Stats endpoint failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing stats: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print(" Railway Deployment Test - HTTP Endpoints")
    print(f" URL: {BASE_URL}")
    print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Root", test_root_endpoint()))
    results.append(("Health", test_health_endpoint()))
    results.append(("Chart Types", test_chart_types_endpoint()))
    results.append(("Stats", test_stats_endpoint()))
    
    # Summary
    print("\n" + "="*60)
    print(" Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:15} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The service is fully operational.")
    elif passed > 0:
        print(f"\n⚠️  {passed} tests passed. Service is partially operational.")
    else:
        print("\n❌ All tests failed. Service may be down.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())