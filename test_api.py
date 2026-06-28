#!/usr/bin/env python3
"""
InventoryPilot API Testing Script
Test all API endpoints and functionality
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_test(name, status, message=""):
    if status:
        print(f"{Colors.GREEN}✓{Colors.END} {name}")
    else:
        print(f"{Colors.RED}✗{Colors.END} {name}")
    if message:
        print(f"  {Colors.CYAN}{message}{Colors.END}")

def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, f"Status: {data['status']}")
            return True
        else:
            print_test("Health Check", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_api_info():
    """Test API info endpoint"""
    print_header("API Information")
    try:
        response = requests.get(f"{BASE_URL}/api/{API_VERSION}/info")
        if response.status_code == 200:
            data = response.json()
            print_test("Get API Info", True, f"Version: {data.get('version', 'N/A')}")
            print(f"\n{Colors.CYAN}Available Endpoints:{Colors.END}")
            for endpoint, path in data.get('endpoints', {}).items():
                print(f"  • {endpoint}: {path}")
            return True
        else:
            print_test("Get API Info", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get API Info", False, str(e))
        return False

def test_analytics():
    """Test analytics endpoint"""
    print_header("Analytics Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/{API_VERSION}/analytics")
        if response.status_code == 200:
            data = response.json()
            print_test("Get Analytics", True)
            print(f"\n{Colors.CYAN}Analytics Summary:{Colors.END}")
            print(f"  • Total Products: {data.get('total_products', 'N/A')}")
            print(f"  • Avg Daily Sales: {data.get('avg_daily_sales', 'N/A'):.2f} units")
            print(f"  • Sales Trend: {data.get('sales_trend', 'N/A')}")
            print(f"  • Inventory Health: {data.get('inventory_health', 'N/A')}")
            print(f"  • Stockout Risk Products: {len(data.get('stockout_risk_products', []))}")
            return True
        else:
            print_test("Get Analytics", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get Analytics", False, str(e))
        return False

def test_prediction():
    """Test prediction endpoint"""
    print_header("Prediction Endpoint")
    try:
        payload = {
            "product_id": "PROD_001",
            "days_ahead": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("Get Prediction", True)
            print(f"\n{Colors.CYAN}Forecast Summary:{Colors.END}")
            print(f"  • Product: {data.get('product_id', 'N/A')}")
            print(f"  • Days Ahead: 30")
            print(f"  • Average Forecast: {data.get('avg_forecast', 'N/A'):.2f} units")
            print(f"  • Peak Forecast: {data.get('peak_forecast', 'N/A'):.2f} units")
            print(f"  • Model Used: {data.get('model_used', 'N/A')}")
            print(f"  • Confidence: {data.get('confidence', 'N/A'):.2%}")
            
            forecast = data.get('forecast', [])
            if forecast:
                print(f"  • First 5 Days: {[f'{x:.0f}' for x in forecast[:5]]}")
            
            return True
        else:
            print_test("Get Prediction", False, f"Status Code: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_test("Get Prediction", False, str(e))
        return False

def test_explanation():
    """Test explanation endpoint"""
    print_header("Explanation Endpoint")
    try:
        payload = {
            "prediction": 150.5,
            "top_features": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/explain",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("Get Explanation", True)
            print(f"\n{Colors.CYAN}Explanation Summary:{Colors.END}")
            print(f"  • Prediction: {data.get('prediction', 'N/A'):.2f} units")
            print(f"  • Business Summary: {data.get('business_summary', 'N/A')}")
            
            drivers = data.get('top_drivers', [])
            if drivers:
                print(f"\n{Colors.CYAN}  Top Drivers:{Colors.END}")
                for driver in drivers[:3]:
                    print(f"    {driver.get('rank', 'N/A')}. {driver.get('feature', 'N/A')}")
                    print(f"       Impact: {driver.get('impact', 'N/A'):.2f}")
                    print(f"       Direction: {driver.get('direction', 'N/A')}")
            
            return True
        else:
            print_test("Get Explanation", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get Explanation", False, str(e))
        return False

def test_business_query():
    """Test business query endpoint"""
    print_header("Business Query Endpoint")
    try:
        payload = {
            "question": "Which products should we reorder?"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("Process Business Query", True)
            print(f"\n{Colors.CYAN}Query Response:{Colors.END}")
            print(f"  • Question: {data.get('question', 'N/A')}")
            print(f"  • Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"\n{Colors.CYAN}Executive Report:{Colors.END}")
            report = data.get('executive_report', 'N/A')
            if report:
                print(f"  {report[:200]}..." if len(report) > 200 else f"  {report}")
            
            return True
        else:
            print_test("Process Business Query", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Process Business Query", False, str(e))
        return False

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     InventoryPilot AI - API Testing Suite                 ║
    ║          Comprehensive API Endpoint Testing               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")
    
    print(f"{Colors.YELLOW}Testing API at: {BASE_URL}{Colors.END}")
    print(f"{Colors.YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Wait for server to be ready
    print(f"\n{Colors.YELLOW}Checking if API is running...{Colors.END}")
    max_retries = 5
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print(f"{Colors.GREEN}✓ API is running{Colors.END}\n")
            break
        except:
            if i < max_retries - 1:
                print(f"  Retry {i+1}/{max_retries}...")
                time.sleep(1)
            else:
                print(f"{Colors.RED}✗ API is not responding. Make sure the backend is running.{Colors.END}")
                print(f"{Colors.YELLOW}Run: python -m uvicorn backend:app --reload{Colors.END}")
                return
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_check()))
    time.sleep(0.5)
    
    results.append(("API Info", test_api_info()))
    time.sleep(0.5)
    
    results.append(("Analytics", test_analytics()))
    time.sleep(0.5)
    
    results.append(("Prediction", test_prediction()))
    time.sleep(0.5)
    
    results.append(("Explanation", test_explanation()))
    time.sleep(0.5)
    
    results.append(("Business Query", test_business_query()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"{Colors.BOLD}Results:{Colors.END}")
    for test_name, result in results:
        status_text = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"  • {test_name}: {status_text}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ All tests passed! API is working correctly.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed. Check the output above for details.{Colors.END}")
    
    print(f"\n{Colors.CYAN}API Documentation: {BASE_URL}/docs{Colors.END}")
    print()

if __name__ == "__main__":
    main()
