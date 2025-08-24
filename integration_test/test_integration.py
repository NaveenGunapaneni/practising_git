"""Main Integration Test Script for GeoPulse Application."""

import pytest
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from config import TEST_USER, OUTPUT_DIR, TEST_CONFIG
from test_data_generator import TestDataGenerator
from api_client import APIClient
from ui_client import UIClient

class TestIntegration:
    """Integration tests for the complete GeoPulse application workflow."""
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Generate test data for all tests."""
        generator = TestDataGenerator()
        files = generator.generate_all_test_data()
        yield files
        # Cleanup will be handled separately
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Create API client for testing."""
        client = APIClient()
        yield client
        client.cleanup()
    
    @pytest.fixture(scope="class")
    def ui_client(self):
        """Create UI client for testing."""
        client = UIClient(headless=True)  # Run in headless mode for CI/CD
        client.start_browser()
        yield client
        client.stop_browser()
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Generate test user data."""
        generator = TestDataGenerator()
        return generator.generate_test_user_data()
    
    def test_01_api_health_check(self, api_client):
        """Test API health endpoint."""
        print("\n🔍 Testing API Health Check...")
        
        try:
            response = api_client.health_check()
            assert response["status"] == "healthy"
            assert "geopulse-api" in response["service"]
            print("✅ API health check passed")
            return True
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False
    
    def test_02_user_registration(self, api_client, test_user):
        """Test user registration through API."""
        print(f"\n👤 Testing User Registration for {test_user['email']}...")
        
        try:
            response = api_client.register_user(test_user)
            assert response["status"] == "success"
            assert "user_id" in response["data"]
            print("✅ User registration passed")
            return True
        except Exception as e:
            print(f"❌ User registration failed: {e}")
            return False
    
    def test_03_user_login(self, api_client, test_user):
        """Test user login through API."""
        print(f"\n🔐 Testing User Login for {test_user['email']}...")
        
        try:
            response = api_client.login_user(test_user["email"], test_user["password"])
            assert response["status"] == "success"
            assert "access_token" in response["data"]
            assert api_client.auth_token is not None
            print("✅ User login passed")
            return True
        except Exception as e:
            print(f"❌ User login failed: {e}")
            return False
    
    def test_04_dashboard_access(self, api_client):
        """Test dashboard access after login."""
        print("\n📊 Testing Dashboard Access...")
        
        try:
            response = api_client.get_dashboard_data()
            assert response["status"] == "success"
            print("✅ Dashboard access passed")
            return True
        except Exception as e:
            print(f"❌ Dashboard access failed: {e}")
            return False
    
    def test_05_file_upload_valid_xlsx(self, api_client, test_data):
        """Test uploading a valid Excel file."""
        print("\n📤 Testing File Upload (Valid XLSX)...")
        
        try:
            file_path = test_data["valid_xlsx"]
            response = api_client.upload_file(file_path, "Test upload from integration test")
            
            assert response["status"] == "success"
            assert "file_id" in response["data"]
            
            file_id = response["data"]["file_id"]
            print(f"✅ File upload passed - File ID: {file_id}")
            return file_id
        except Exception as e:
            print(f"❌ File upload failed: {e}")
            return None
    
    def test_06_file_processing_wait(self, api_client, file_id):
        """Wait for file processing to complete."""
        if not file_id:
            print("⏭️ Skipping file processing test - no file ID")
            return None
        
        print(f"\n⏳ Waiting for File Processing (File ID: {file_id})...")
        
        try:
            status_response = api_client.wait_for_file_processing(file_id, max_wait=120)
            assert status_response["status"] == "success"
            
            final_status = status_response["data"]["status"]
            assert final_status == "completed"
            
            print(f"✅ File processing completed - Status: {final_status}")
            return file_id
        except Exception as e:
            print(f"❌ File processing failed: {e}")
            return None
    
    def test_07_file_download(self, api_client, file_id):
        """Test downloading the processed file."""
        if not file_id:
            print("⏭️ Skipping file download test - no file ID")
            return None
        
        print(f"\n📥 Testing File Download (File ID: {file_id})...")
        
        try:
            output_path = OUTPUT_DIR / f"downloaded_file_{file_id}.xlsx"
            downloaded_path = api_client.download_file(file_id, output_path)
            
            assert downloaded_path.exists()
            assert downloaded_path.suffix == ".xlsx"
            
            print(f"✅ File download passed - Saved to: {downloaded_path}")
            return downloaded_path
        except Exception as e:
            print(f"❌ File download failed: {e}")
            return None
    
    def test_08_downloaded_file_validation(self, api_client, downloaded_path):
        """Validate the downloaded file format and content."""
        if not downloaded_path:
            print("⏭️ Skipping file validation test - no downloaded file")
            return False
        
        print(f"\n🔍 Validating Downloaded File: {downloaded_path.name}...")
        
        try:
            validation_result = api_client.validate_downloaded_file(downloaded_path, "xlsx")
            
            assert validation_result["valid"] == True
            assert validation_result["rows"] > 0
            assert validation_result["has_required_columns"] == True
            assert "latitude" in validation_result["columns"]
            assert "longitude" in validation_result["columns"]
            assert "date" in validation_result["columns"]
            assert "value" in validation_result["columns"]
            
            print(f"✅ File validation passed:")
            print(f"   - Rows: {validation_result['rows']}")
            print(f"   - Columns: {validation_result['columns']}")
            print(f"   - File size: {validation_result['file_size_mb']:.2f} MB")
            print(f"   - Has required columns: {validation_result['has_required_columns']}")
            
            return True
        except Exception as e:
            print(f"❌ File validation failed: {e}")
            return False
    
    def test_09_ui_registration(self, ui_client, test_user):
        """Test user registration through UI."""
        print(f"\n🌐 Testing UI Registration for {test_user['email']}...")
        
        try:
            success = ui_client.register_user(test_user)
            assert success == True
            print("✅ UI registration passed")
            return True
        except Exception as e:
            print(f"❌ UI registration failed: {e}")
            return False
    
    def test_10_ui_login(self, ui_client, test_user):
        """Test user login through UI."""
        print(f"\n🌐 Testing UI Login for {test_user['email']}...")
        
        try:
            success = ui_client.login_user(test_user["email"], test_user["password"])
            assert success == True
            print("✅ UI login passed")
            return True
        except Exception as e:
            print(f"❌ UI login failed: {e}")
            return False
    
    def test_11_ui_dashboard_check(self, ui_client):
        """Test dashboard accessibility through UI."""
        print("\n🌐 Testing UI Dashboard...")
        
        try:
            dashboard_info = ui_client.check_dashboard()
            assert dashboard_info["accessible"] == True
            print("✅ UI dashboard check passed")
            return True
        except Exception as e:
            print(f"❌ UI dashboard check failed: {e}")
            return False
    
    def test_12_ui_file_upload(self, ui_client, test_data):
        """Test file upload through UI."""
        print("\n🌐 Testing UI File Upload...")
        
        try:
            file_path = test_data["valid_xlsx"]
            success = ui_client.upload_file(file_path, "UI test upload")
            assert success == True
            print("✅ UI file upload passed")
            return True
        except Exception as e:
            print(f"❌ UI file upload failed: {e}")
            return False
    
    def test_13_ui_logout(self, ui_client):
        """Test logout through UI."""
        print("\n🌐 Testing UI Logout...")
        
        try:
            success = ui_client.logout()
            assert success == True
            print("✅ UI logout passed")
            return True
        except Exception as e:
            print(f"❌ UI logout failed: {e}")
            return False
    
    def test_14_error_handling_invalid_file(self, api_client, test_data):
        """Test error handling for invalid file upload."""
        print("\n🚫 Testing Error Handling (Invalid File)...")
        
        try:
            file_path = test_data["invalid_format"]
            response = api_client.upload_file(file_path, "Invalid file test")
            
            # Should return an error response
            assert response["status"] == "error" or "error" in response
            print("✅ Invalid file error handling passed")
            return True
        except Exception as e:
            print(f"❌ Invalid file error handling failed: {e}")
            return False
    
    def test_15_error_handling_malformed_data(self, api_client, test_data):
        """Test error handling for malformed data file."""
        print("\n🚫 Testing Error Handling (Malformed Data)...")
        
        try:
            file_path = test_data["malformed_data"]
            response = api_client.upload_file(file_path, "Malformed data test")
            
            # Should return an error response
            assert response["status"] == "error" or "error" in response
            print("✅ Malformed data error handling passed")
            return True
        except Exception as e:
            print(f"❌ Malformed data error handling failed: {e}")
            return False


def run_integration_tests():
    """Run the complete integration test suite."""
    print("🚀 Starting GeoPulse Integration Tests")
    print("=" * 50)
    
    # Create test instance
    test_instance = TestIntegration()
    
    # Initialize test data
    print("📊 Initializing test data...")
    test_data = test_instance.test_data()
    
    # Initialize clients
    print("🔧 Initializing test clients...")
    api_client = test_instance.api_client()
    ui_client = test_instance.ui_client()
    test_user = test_instance.test_user()
    
    # Test results tracking
    results = {
        "start_time": datetime.now().isoformat(),
        "tests": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    }
    
    # Run tests in sequence
    test_methods = [
        ("API Health Check", test_instance.test_01_api_health_check),
        ("User Registration", test_instance.test_02_user_registration),
        ("User Login", test_instance.test_03_user_login),
        ("Dashboard Access", test_instance.test_04_dashboard_access),
        ("File Upload", test_instance.test_05_file_upload_valid_xlsx),
        ("File Processing", test_instance.test_06_file_processing_wait),
        ("File Download", test_instance.test_07_file_download),
        ("File Validation", test_instance.test_08_downloaded_file_validation),
        ("UI Registration", test_instance.test_09_ui_registration),
        ("UI Login", test_instance.test_10_ui_login),
        ("UI Dashboard", test_instance.test_11_ui_dashboard_check),
        ("UI File Upload", test_instance.test_12_ui_file_upload),
        ("UI Logout", test_instance.test_13_ui_logout),
        ("Invalid File Error", test_instance.test_14_error_handling_invalid_file),
        ("Malformed Data Error", test_instance.test_15_error_handling_malformed_data),
    ]
    
    file_id = None
    downloaded_path = None
    
    for test_name, test_method in test_methods:
        results["summary"]["total"] += 1
        
        try:
            if "file_upload" in test_name.lower():
                result = test_method(api_client, test_data)
                if result:
                    file_id = result
            elif "file_processing" in test_name.lower():
                result = test_method(api_client, file_id)
                if result:
                    file_id = result
            elif "file_download" in test_name.lower():
                result = test_method(api_client, file_id)
                if result:
                    downloaded_path = result
            elif "file_validation" in test_name.lower():
                result = test_method(api_client, downloaded_path)
            elif "ui_" in test_name.lower():
                if "registration" in test_name.lower():
                    result = test_method(ui_client, test_user)
                elif "login" in test_name.lower():
                    result = test_method(ui_client, test_user)
                elif "dashboard" in test_name.lower():
                    result = test_method(ui_client)
                elif "file_upload" in test_name.lower():
                    result = test_method(ui_client, test_data)
                elif "logout" in test_name.lower():
                    result = test_method(ui_client)
            elif "error_handling" in test_name.lower():
                result = test_method(api_client, test_data)
            else:
                result = test_method(api_client)
            
            if result:
                results["tests"][test_name] = {"status": "passed", "result": result}
                results["summary"]["passed"] += 1
            else:
                results["tests"][test_name] = {"status": "failed", "result": None}
                results["summary"]["failed"] += 1
                
        except Exception as e:
            results["tests"][test_name] = {"status": "failed", "error": str(e)}
            results["summary"]["failed"] += 1
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Generate test report
    results["end_time"] = datetime.now().isoformat()
    
    # Save results to file
    report_path = OUTPUT_DIR / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']} ✅")
    print(f"Failed: {results['summary']['failed']} ❌")
    print(f"Skipped: {results['summary']['skipped']} ⏭️")
    print(f"Success Rate: {(results['summary']['passed'] / results['summary']['total'] * 100):.1f}%")
    print(f"Report saved to: {report_path}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    generator = TestDataGenerator()
    generator.cleanup_test_data()
    
    # Return success if all tests passed
    return results["summary"]["failed"] == 0


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
