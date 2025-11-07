#!/usr/bin/env python3
"""
Simple test script for the Parking API endpoints.
Run this after starting the API to verify it's working correctly.
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_create_spot():
    """Test creating a parking spot."""
    print("\nTesting spot creation...")

    spot_data = {
        "user_id": "test_user_123",
        "lat": 34.020882,
        "lon": -6.841650,
        "type": "leaving",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    response = requests.post(f"{BASE_URL}/api/v1/spot", json=spot_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        return response.json()["spot_id"]
    return None

def test_get_spots():
    """Test fetching spots."""
    print("\nTesting spot retrieval...")

    params = {
        "lat": 34.020882,
        "lon": -6.841650,
        "radius_meters": 1000
    }

    response = requests.get(f"{BASE_URL}/api/v1/spots", params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    """Run all tests."""
    print("Testing Parking API...")
    print("=" * 50)

    try:
        # Test health check
        if not test_health_check():
            print("❌ Health check failed")
            return
        print("✅ Health check passed")

        # Test spot creation
        spot_id = test_create_spot()
        if spot_id:
            print("✅ Spot creation passed")
        else:
            print("❌ Spot creation failed")
            return

        # Test spot retrieval
        if test_get_spots():
            print("✅ Spot retrieval passed")
        else:
            print("❌ Spot retrieval failed")
            return

        print("\n🎉 All tests passed!")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
