"""
Settings module to load and provide access to configuration from YAML files.
"""
import os
from pathlib import Path

import yaml


class Settings:
    """Load and provide access to configuration settings."""
    
    def __init__(self, env="test11"):
        """
        Initialize settings by loading configuration from YAML file.
        
        Args:
            env: Environment name (test11, test12, silo, prod, qa, etc.)
        """
        self.env = env
        self.config_path = Path(__file__).parent.parent / "config" / f"env.{env}.yaml"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    @property
    def base_url(self):
        """Get base URL for the application."""
        return self.config['application']['base_url']
    
    @property
    def login_url(self):
        """Get login URL for the application."""
        return self.config['application'].get('login_url', self.base_url)
    
    @property
    def timeout(self):
        """Get default timeout in milliseconds."""
        return self.config['application']['timeout']
    
    @property
    def browser_type(self):
        """Get browser type (chromium, firefox, webkit)."""
        return self.config['browser']['browser_type']
    
    @property
    def headless(self):
        """Check if browser should run in headless mode."""
        return self.config['browser']['headless']
    
    @property
    def viewport(self):
        """Get viewport dimensions."""
        return self.config['browser']['viewport']
    
    @property
    def browser_args(self):
        """Get browser launch arguments."""
        return self.config['browser'].get('args', [])
    
    @property
    def test_data_csv(self):
        """Get path to test data CSV file."""
        base_path = Path(__file__).parent.parent
        return base_path / self.config['data']['test_data_csv']
    
    @property
    def allure_results_dir(self):
        """Get Allure results directory."""
        base_path = Path(__file__).parent.parent
        return base_path / self.config['reporting']['allure_results']


# Singleton instance
settings = Settings(env=os.getenv('TEST_ENV', 'test11'))
