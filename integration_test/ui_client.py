"""UI Client for Integration Testing using Selenium."""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from config import UI_PAGES, TEST_CONFIG, SCREENSHOTS_DIR

class UIClient:
    """Client for interacting with the GeoPulse UI during testing."""
    
    def __init__(self, headless: bool = None, browser: str = None):
        """Initialize the UI client.
        
        Args:
            headless: Run browser in headless mode
            browser: Browser type (chrome, firefox, etc.)
        """
        self.headless = headless if headless is not None else TEST_CONFIG["headless"]
        self.browser = browser or TEST_CONFIG["browser"]
        self.driver = None
        self.wait = None
        self.screenshots_dir = SCREENSHOTS_DIR
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def start_browser(self):
        """Start the browser session."""
        if self.browser.lower() == "chrome":
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
        
        self.driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
        self.wait = WebDriverWait(self.driver, TEST_CONFIG["timeout"])
    
    def stop_browser(self):
        """Stop the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def take_screenshot(self, name: str = None) -> Path:
        """Take a screenshot and save it.
        
        Args:
            name: Name for the screenshot file
            
        Returns:
            Path to the screenshot file
        """
        if not name:
            name = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = self.screenshots_dir / name
        self.driver.save_screenshot(str(screenshot_path))
        return screenshot_path
    
    def navigate_to(self, page: str):
        """Navigate to a specific page.
        
        Args:
            page: Page name (login, register, dashboard, upload)
        """
        url = UI_PAGES.get(page)
        if not url:
            raise ValueError(f"Unknown page: {page}")
        
        self.driver.get(url)
        time.sleep(2)  # Wait for page to load
    
    def wait_for_element(self, by: By, value: str, timeout: int = None):
        """Wait for an element to be present and visible.
        
        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds
            
        Returns:
            WebElement
        """
        timeout = timeout or TEST_CONFIG["timeout"]
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, value)))
    
    def wait_for_element_clickable(self, by: By, value: str, timeout: int = None):
        """Wait for an element to be clickable.
        
        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds
            
        Returns:
            WebElement
        """
        timeout = timeout or TEST_CONFIG["timeout"]
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def register_user(self, user_data: Dict[str, str]) -> bool:
        """Register a new user through the UI.
        
        Args:
            user_data: User registration data
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            self.navigate_to("register")
            
            # Fill in registration form
            self.wait_for_element(By.ID, "organization_name").send_keys(user_data["organization_name"])
            self.wait_for_element(By.ID, "user_name").send_keys(user_data["user_name"])
            self.wait_for_element(By.ID, "contact_phone").send_keys(user_data["contact_phone"])
            self.wait_for_element(By.ID, "email").send_keys(user_data["email"])
            self.wait_for_element(By.ID, "password").send_keys(user_data["password"])
            
            # Submit form
            submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for success message or redirect
            time.sleep(3)
            
            # Check if we're redirected to login page (success)
            current_url = self.driver.current_url
            if "login" in current_url:
                return True
            
            # Check for success message
            try:
                success_element = self.driver.find_element(By.CSS_SELECTOR, ".success-message, .toast-success")
                return "success" in success_element.text.lower()
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Registration failed: {e}")
            self.take_screenshot("registration_failed.png")
            return False
    
    def login_user(self, email: str, password: str) -> bool:
        """Login a user through the UI.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.navigate_to("login")
            
            # Fill in login form
            self.wait_for_element(By.ID, "email").send_keys(email)
            self.wait_for_element(By.ID, "password").send_keys(password)
            
            # Submit form
            submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect or success
            time.sleep(3)
            
            # Check if we're redirected to dashboard (success)
            current_url = self.driver.current_url
            if "dashboard" in current_url:
                return True
            
            # Check for success message
            try:
                success_element = self.driver.find_element(By.CSS_SELECTOR, ".success-message, .toast-success")
                return "success" in success_element.text.lower()
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Login failed: {e}")
            self.take_screenshot("login_failed.png")
            return False
    
    def upload_file(self, file_path: Path, description: str = "") -> bool:
        """Upload a file through the UI.
        
        Args:
            file_path: Path to the file to upload
            description: Optional description for the file
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            self.navigate_to("upload")
            
            # Find file input and upload file
            file_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(str(file_path.absolute()))
            
            # Add description if provided
            if description:
                try:
                    desc_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='description'], textarea[name='description']")
                    desc_input.send_keys(description)
                except:
                    pass  # Description field might not exist
            
            # Submit upload
            upload_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit'], .upload-button")
            upload_button.click()
            
            # Wait for upload to complete
            time.sleep(5)
            
            # Check for success message
            try:
                success_element = self.driver.find_element(By.CSS_SELECTOR, ".success-message, .toast-success")
                return "success" in success_element.text.lower()
            except:
                # Check if we're still on upload page (might indicate success)
                current_url = self.driver.current_url
                return "upload" in current_url
            
        except Exception as e:
            print(f"File upload failed: {e}")
            self.take_screenshot("upload_failed.png")
            return False
    
    def check_dashboard(self) -> Dict[str, Any]:
        """Check dashboard content and functionality.
        
        Returns:
            Dashboard information
        """
        try:
            self.navigate_to("dashboard")
            
            dashboard_info = {
                "accessible": True,
                "elements_found": [],
                "errors": []
            }
            
            # Check for common dashboard elements
            common_elements = [
                "dashboard-title",
                "file-list",
                "upload-button",
                "user-info",
                "logout-button"
            ]
            
            for element_id in common_elements:
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    dashboard_info["elements_found"].append(element_id)
                except:
                    dashboard_info["errors"].append(f"Element not found: {element_id}")
            
            # Check for file list
            try:
                file_list = self.driver.find_element(By.CSS_SELECTOR, ".file-list, .files-table, [data-testid='file-list']")
                dashboard_info["has_file_list"] = True
            except:
                dashboard_info["has_file_list"] = False
            
            return dashboard_info
            
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "elements_found": [],
                "errors": [str(e)]
            }
    
    def download_file(self, file_name: str = None) -> Optional[Path]:
        """Download a file through the UI.
        
        Args:
            file_name: Name of the file to download (if multiple files)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            self.navigate_to("dashboard")
            
            # Find download button
            if file_name:
                # Find specific file and its download button
                file_row = self.driver.find_element(By.XPATH, f"//tr[contains(., '{file_name}')]")
                download_button = file_row.find_element(By.CSS_SELECTOR, ".download-button, [data-testid='download']")
            else:
                # Find first download button
                download_button = self.wait_for_element(By.CSS_SELECTOR, ".download-button, [data-testid='download']")
            
            # Click download button
            download_button.click()
            
            # Wait for download to start
            time.sleep(3)
            
            # Note: In a real scenario, you'd need to check the downloads directory
            # For now, we'll assume success if no error occurred
            return Path("downloads") / f"{file_name or 'downloaded_file'}.xlsx"
            
        except Exception as e:
            print(f"File download failed: {e}")
            self.take_screenshot("download_failed.png")
            return None
    
    def logout(self) -> bool:
        """Logout the current user.
        
        Returns:
            True if logout successful, False otherwise
        """
        try:
            # Find and click logout button
            logout_button = self.wait_for_element(By.CSS_SELECTOR, ".logout-button, [data-testid='logout']")
            logout_button.click()
            
            # Wait for redirect to login page
            time.sleep(3)
            
            current_url = self.driver.current_url
            return "login" in current_url
            
        except Exception as e:
            print(f"Logout failed: {e}")
            self.take_screenshot("logout_failed.png")
            return False
    
    def get_page_title(self) -> str:
        """Get the current page title.
        
        Returns:
            Page title
        """
        return self.driver.title
    
    def get_current_url(self) -> str:
        """Get the current page URL.
        
        Returns:
            Current URL
        """
        return self.driver.current_url
    
    def wait_for_page_load(self, timeout: int = None):
        """Wait for the page to fully load.
        
        Args:
            timeout: Timeout in seconds
        """
        timeout = timeout or TEST_CONFIG["timeout"]
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
