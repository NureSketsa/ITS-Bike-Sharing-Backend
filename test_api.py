#!/usr/bin/env python3
"""
Complete JWT API Testing Script for ITS Bike Sharing Backend
This script handles dynamic registration, JWT authentication, and tests all endpoints systematically.
"""

import requests
import json
import time
from datetime import datetime

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

# --- API Test Class ---
class BikeAPI:
    """A class to encapsulate API testing operations."""
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {'Content-Type': 'application/json'}

    def register(self, user_data):
        """Register a new user."""
        print(f"📝 Attempting to register new user with NRP: {user_data['nrp']}...")
        try:
            response = requests.post(f"{self.base_url}/api/auth/register",
                                     json=user_data,
                                     headers=self.headers)
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Registration successful!")
                return True
            # Handle case where user already exists, which is also a form of success for testing
            elif response.status_code == 400 and "already exists" in response.text:
                print("👍 User already exists. Proceeding with login.")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False

    def login(self, nrp, password):
        """Login and get JWT token."""
        print(f"🔐 Attempting to login with NRP: {nrp}...")
        login_data = {"nrp": nrp, "password": password}
        try:
            response = requests.post(f"{self.base_url}/api/auth/login",
                                     json=login_data,
                                     headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.headers['Authorization'] = f'Bearer {self.token}'
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def test_endpoint(self, method, path, data=None, expected_status=200, description=""):
        """Test a single API endpoint."""
        # Note: The base prefix /api/transaksi is now part of the path
        url = f"{self.base_url}{path}"
        print(f"\n🔥 Testing {method} {url}")
        if description:
            print(f"📝 {description}")
        if data:
            print(f"📤 Sending data: {json.dumps(data, indent=2)}")

        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            print(f"📨 Status Code: {response.status_code}")
            try:
                response_json = response.json()
                print(f"📄 Response: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                print(f"📄 Response (text): {response.text}")

            success = response.status_code == expected_status
            if success:
                print("✅ TEST PASSED")
            else:
                print(f"❌ TEST FAILED - Expected {expected_status}, got {response.status_code}")
            return success, response
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR - Make sure your Flask server is running!")
            return False, None
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False, None

# --- Helper Functions ---
def print_separator(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

# --- Main Test Runner ---
def run_comprehensive_tests():
    """Run all API tests, including dynamic registration."""
    print_separator("ITS BIKE SHARING API - COMPREHENSIVE TESTING")
    api = BikeAPI()
    results = []

    # --- Step 1: Dynamic User Registration ---
    print_separator("STEP 1: DYNAMIC REGISTRATION")
    # Create a unique user for this test run
    timestamp = int(datetime.now().timestamp())
    unique_nrp = f"testuser{timestamp}"
    new_user_data = {
        "nrp": unique_nrp,
        "nama": f"Test User {timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "password123"
    }
    if not api.register(new_user_data):
        print("\n❌ Critical failure: Cannot register a new user. Aborting tests.")
        return

    # --- Step 2: Authentication ---
    print_separator("STEP 2: AUTHENTICATION")
    if not api.login(new_user_data['nrp'], new_user_data['password']):
        print("\n❌ Critical failure: Cannot log in with newly registered user. Aborting tests.")
        return

    # --- Step 3: Test Transaction Endpoints ---
    print_separator("STEP 3: TRANSACTION & RENTAL TESTS")

    # Check for active rentals (should be none)
    success, _ = api.test_endpoint("GET", "/api/transaksi/active", description="Check for active rental (initially)")
    results.append(("Initial Active Rental Check", success))

    # Create a new rental
    rental_data = {"kendaraan_id": 2, "stasiun_ambil_id": 1}
    success, rental_response = api.test_endpoint("POST", "/api/transaksi/rent", rental_data, 201, "Create a new rental")
    results.append(("Create Rental", success))

    # Check for active rentals again (should find one)
    success, _ = api.test_endpoint("GET", "/api/transaksi/active", description="Check for active rental (after renting)")
    results.append(("Second Active Rental Check", success))

    # Get rental ID for the return test
    transaksi_id = None
    if success and rental_response:
        try:
            transaksi_id = rental_response.json().get('transaksi', {}).get('transaksi_id')
        except:
            pass

    # Return the bike
    if transaksi_id:
        return_data = {"transaksi_id": transaksi_id, "stasiun_kembali_id": 1}
        success, _ = api.test_endpoint("POST", "/api/transaksi/return", return_data, 200, "Return the bike")
        results.append(("Return Bike", success))
    else:
        print("⚠️ Skipping return test - could not get transaksi_id from rental response")
        results.append(("Return Bike", False))

    # Check for active rentals a final time (should be none again)
    success, _ = api.test_endpoint("GET", "/api/transaksi/active", description="Check for active rental (after returning)")
    results.append(("Final Active Rental Check", success))

    # --- Summary ---
    print_separator("TEST RESULTS SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"📊 Tests Passed: {passed}/{total}")
    if total > 0:
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

    print("\n📋 Detailed Results:")
    for test_name, success_status in results:
        status = "✅ PASS" if success_status else "❌ FAIL"
        print(f"  {status} - {test_name}")

    if passed == total:
        print("\n🎉🎉🎉 ALL TESTS PASSED! Your API is solid! 🎉🎉🎉")
    else:
        print("\n⚠️ Some tests failed. Please review the detailed output above.")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("⚠️ Make sure your Flask server is running on http://127.0.0.1:5000")
    print("⚠️ Make sure you have at least one stasiun and one kendaraan in your database.")
    time.sleep(2)
    run_comprehensive_tests()
