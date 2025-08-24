#!/usr/bin/env python3
"""Simple runner script for GeoPulse Integration Tests."""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from test_integration import run_integration_tests

def main():
    """Main function to run integration tests."""
    print("🚀 GeoPulse Integration Test Runner")
    print("=" * 40)
    
    # Check if Docker services are running
    print("🔍 Checking if Docker services are running...")
    
    try:
        import requests
        # Check API health
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API is not responding correctly")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure Docker services are running with: docker-compose up -d")
        return 1
    
    try:
        # Check UI
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("✅ UI is running")
        else:
            print("❌ UI is not responding correctly")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to UI: {e}")
        print("💡 Make sure Docker services are running with: docker-compose up -d")
        return 1
    
    print("\n🎯 Starting integration tests...")
    
    # Run the integration tests
    success = run_integration_tests()
    
    if success:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print("\n💥 Some integration tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
