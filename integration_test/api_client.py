"""API Client for Integration Testing."""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
from config import API_ENDPOINTS, TEST_CONFIG, RESPONSE_SCHEMAS
import jsonschema

class APIClient:
    """Client for interacting with the GeoPulse API during testing."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or API_ENDPOINTS["health"].replace("/api/v1/health", "")
        self.timeout = timeout or TEST_CONFIG["timeout"]
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
    
    def set_auth_token(self, token: str):
        """Set the authentication token for subsequent requests."""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def clear_auth_token(self):
        """Clear the authentication token."""
        self.auth_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status.
        
        Returns:
            Health check response
        """
        response = self._make_request("GET", "/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Registration response
        """
        response = self._make_request(
            "POST", 
            "/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login a user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Login response with token
        """
        form_data = {
            "username": email,
            "password": password
        }
        
        response = self._make_request(
            "POST",
            "/api/v1/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        login_data = response.json()
        
        # Store token for subsequent requests
        if login_data.get("status") == "success":
            token = login_data["data"]["access_token"]
            self.set_auth_token(token)
            self.user_data = login_data["data"]["user"]
        
        return login_data
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for the authenticated user.
        
        Returns:
            Dashboard data
        """
        if not self.auth_token:
            raise Exception("Authentication required for dashboard access")
        
        response = self._make_request("GET", "/api/v1/dashboard")
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path: Path, description: str = "") -> Dict[str, Any]:
        """Upload a file for processing.
        
        Args:
            file_path: Path to the file to upload
            description: Optional description for the file
            
        Returns:
            Upload response
        """
        if not self.auth_token:
            raise Exception("Authentication required for file upload")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {'description': description} if description else {}
            
            response = self._make_request(
                "POST",
                "/api/v1/files/upload",
                files=files,
                data=data
            )
        
        response.raise_for_status()
        return response.json()
    
    def list_files(self) -> Dict[str, Any]:
        """List uploaded files for the authenticated user.
        
        Returns:
            List of files
        """
        if not self.auth_token:
            raise Exception("Authentication required for file listing")
        
        response = self._make_request("GET", "/api/v1/files/list")
        response.raise_for_status()
        return response.json()
    
    def get_file_status(self, file_id: int) -> Dict[str, Any]:
        """Get the status of a file processing job.
        
        Args:
            file_id: ID of the file
            
        Returns:
            File status
        """
        if not self.auth_token:
            raise Exception("Authentication required for file status")
        
        response = self._make_request("GET", f"/api/v1/files/status/{file_id}")
        response.raise_for_status()
        return response.json()
    
    def download_file(self, file_id: int, output_path: Path) -> Path:
        """Download a processed file.
        
        Args:
            file_id: ID of the file to download
            output_path: Path where to save the downloaded file
            
        Returns:
            Path to the downloaded file
        """
        if not self.auth_token:
            raise Exception("Authentication required for file download")
        
        response = self._make_request("GET", f"/api/v1/files/{file_id}/download")
        response.raise_for_status()
        
        # Save the file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    def view_file(self, file_id: int) -> Dict[str, Any]:
        """View file details and preview.
        
        Args:
            file_id: ID of the file to view
            
        Returns:
            File details
        """
        if not self.auth_token:
            raise Exception("Authentication required for file viewing")
        
        response = self._make_request("GET", f"/api/v1/files/{file_id}/view")
        response.raise_for_status()
        return response.json()
    
    def validate_response_schema(self, response_data: Dict[str, Any], schema_type: str = "success"):
        """Validate response against expected schema.
        
        Args:
            response_data: Response data to validate
            schema_type: Type of schema to validate against ("success" or "error")
            
        Returns:
            True if valid, raises exception if invalid
        """
        schema = RESPONSE_SCHEMAS.get(schema_type)
        if not schema:
            raise ValueError(f"Unknown schema type: {schema_type}")
        
        try:
            jsonschema.validate(instance=response_data, schema=schema)
            return True
        except jsonschema.ValidationError as e:
            raise Exception(f"Response validation failed: {e}")
    
    def wait_for_file_processing(self, file_id: int, max_wait: int = 300, check_interval: int = 10) -> Dict[str, Any]:
        """Wait for file processing to complete.
        
        Args:
            file_id: ID of the file to monitor
            max_wait: Maximum time to wait in seconds
            check_interval: Interval between status checks in seconds
            
        Returns:
            Final file status
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = self.get_file_status(file_id)
            
            if status_response.get("status") == "success":
                status = status_response.get("data", {}).get("status")
                
                if status in ["completed", "failed"]:
                    return status_response
                
                if status == "processing":
                    print(f"⏳ File {file_id} is still processing...")
                else:
                    print(f"📊 File {file_id} status: {status}")
            
            time.sleep(check_interval)
        
        raise TimeoutError(f"File processing timeout after {max_wait} seconds")
    
    def validate_downloaded_file(self, file_path: Path, expected_format: str = "xlsx") -> Dict[str, Any]:
        """Validate a downloaded file.
        
        Args:
            file_path: Path to the downloaded file
            expected_format: Expected file format
            
        Returns:
            Validation results
        """
        if not file_path.exists():
            return {"valid": False, "error": "File does not exist"}
        
        try:
            if expected_format.lower() == "xlsx":
                df = pd.read_excel(file_path)
            elif expected_format.lower() == "csv":
                df = pd.read_csv(file_path)
            else:
                return {"valid": False, "error": f"Unsupported format: {expected_format}"}
            
            # Basic validation
            validation_result = {
                "valid": True,
                "rows": len(df),
                "columns": list(df.columns),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
                "has_required_columns": all(col in df.columns for col in ["latitude", "longitude", "date", "value"]),
                "data_types": df.dtypes.to_dict()
            }
            
            return validation_result
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def cleanup(self):
        """Clean up the API client."""
        self.session.close()
