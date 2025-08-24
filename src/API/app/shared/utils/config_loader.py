"""Configuration loader utility for external configuration files."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings


class ConfigLoader:
    """Utility class for loading configuration from external files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config loader.
        
        Args:
            config_path: Path to configuration directory. If None, uses settings.config_path.
        """
        self.config_path = Path(config_path or settings.config_path)
    
    def load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from a YAML file.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing the configuration
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
        """
        config_file = self.config_path / filename
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {config_file}: {e}")
    
    def load_sentinel_hub_config(self) -> Dict[str, Any]:
        """Load Sentinel Hub configuration.
        
        Returns:
            Dictionary containing Sentinel Hub configuration
        """
        try:
            config = self.load_yaml_config('sentinel_hub.yaml')
            return config.get('sentinel_hub', {})
        except FileNotFoundError:
            # Return default configuration if file doesn't exist
            return {
                'client_id': os.getenv('SENTINEL_HUB_CLIENT_ID', ''),
                'client_secret': os.getenv('SENTINEL_HUB_CLIENT_SECRET', ''),
                'instance_id': os.getenv('SENTINEL_HUB_INSTANCE_ID', ''),
                'oauth_url': 'https://services.sentinel-hub.com/oauth/token',
                'api_url': 'https://services.sentinel-hub.com/api/v1',
                'default_resolution': 10,
                'default_crs': 'EPSG:4326',
                'timeout': 300,
                'max_retries': 3
            }
    
    def load_app_config(self) -> Dict[str, Any]:
        """Load application configuration.
        
        Returns:
            Dictionary containing application configuration
        """
        try:
            return self.load_yaml_config('app_config.yaml')
        except FileNotFoundError:
            # Return default configuration if file doesn't exist
            return {
                'app': {
                    'name': 'GeoPulse',
                    'version': '1.0.0',
                    'environment': 'development'
                },
                'upload': {
                    'max_file_size_mb': 50,
                    'allowed_extensions': ['.xlsx', '.csv', '.xls'],
                    'temp_dir': '/app/user_data/temp',
                    'upload_dir': '/app/user_data/uploads'
                },
                'processing': {
                    'max_concurrent_jobs': 5,
                    'timeout_minutes': 30,
                    'output_dir': '/app/output'
                },
                'database': {
                    'pool_size': 20,
                    'max_overflow': 30,
                    'pool_timeout': 30,
                    'pool_recycle': 3600
                },
                'logging': {
                    'level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'file': '/app/logs/api.log',
                    'max_size_mb': 100,
                    'backup_count': 5
                }
            }
    
    def get_output_path(self, subdirectory: str = '') -> Path:
        """Get the output path for a specific subdirectory.
        
        Args:
            subdirectory: Optional subdirectory within the output path
            
        Returns:
            Path object for the output directory
        """
        output_path = Path(settings.output_path)
        if subdirectory:
            output_path = output_path / subdirectory
        
        # Create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def get_data_path(self, subdirectory: str = '') -> Path:
        """Get the data path for a specific subdirectory.
        
        Args:
            subdirectory: Optional subdirectory within the data path
            
        Returns:
            Path object for the data directory
        """
        data_path = Path(settings.data_path)
        if subdirectory:
            data_path = data_path / subdirectory
        
        # Create directory if it doesn't exist
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path
    
    def ensure_directories_exist(self):
        """Ensure all necessary directories exist."""
        directories = [
            Path(settings.config_path),
            Path(settings.data_path),
            Path(settings.output_path),
            Path(settings.upload_dir),
            Path(settings.upload_temp_dir),
            Path(settings.log_file).parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global config loader instance
config_loader = ConfigLoader()
