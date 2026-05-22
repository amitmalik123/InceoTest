"""
Centralized Configuration Manager
Single source of truth for all configuration loading across the framework
Eliminates config loading duplication in ApiClientFactory, DatabaseClientFactory, and conftest.py
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from framework.common.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Singleton configuration manager for centralized config handling
    
    Features:
    - Single source of truth for configuration loading
    - Automatic environment detection from ENV_NAME
    - Environment variable substitution in config values
    - Lazy loading with caching
    - Thread-safe singleton pattern
    """
    _instance = None
    _config = None
    _env_name = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize config manager and load .env file"""
        if self._config is None:
            load_dotenv()  # Load .env file if present
            self._load_config()
    
    def _get_env_name(self) -> str:
        """
        Get environment name from ENV_NAME variable
        
        Priority:
        1. Cached value (if already loaded)
        2. Environment variable ENV_NAME
        3. .env file ENV_NAME entry
        4. Default to 'default'
        
        Returns:
            Environment name string
        """
        if self._env_name:
            return self._env_name
        
        # Try environment variable first
        env_name = os.environ.get('ENV_NAME', '').strip()
        
        # If not found, try reading from .env file
        if not env_name:
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as env_file:
                    for line in env_file:
                        if line.strip().startswith('ENV_NAME='):
                            env_name = line.strip().split('=', 1)[1].strip()
                            break
        
        self._env_name = env_name if env_name else None
        return self._env_name or 'default'
    
    def _load_config(self):
        """
        Load configuration from YAML file
        
        File resolution:
        1. config/config.{ENV_NAME}.yaml (e.g., config.T12.yaml)
        2. config/config.yaml (fallback)
        """
        env_name = self._get_env_name()
        
        # Try environment-specific config first (skip if default)
        config_path = None
        if env_name != 'default':
            config_path = f'config/config.{env_name}.yaml'
            if not os.path.exists(config_path):
                logger.warning(f"Environment-specific config not found: {config_path}")
                config_path = None
        
        # Fallback to default config
        if not config_path:
            config_path = 'config/config.yaml'
        
        if not os.path.exists(config_path):
            logger.error(f"No config file found at {config_path}")
            self._config = {}
            return
        
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
                logger.info(f"[OK] Loaded configuration from: {config_path} (ENV: {env_name})")
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            self._config = {}
    
    def get_config(self, reload: bool = False) -> Dict:
        """
        Get the loaded configuration dictionary
        
        Args:
            reload: Force reload configuration from file
        
        Returns:
            Configuration dictionary
        """
        if reload or self._config is None:
            self._config = None
            self._env_name = None
            self._load_config()
        return self._config
    
    def get(self, key: str, default=None):
        """
        Get a specific configuration value
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            config.get('api_endpoints.parties.base_url')
        """
        if self._config is None:
            self._load_config()
        
        # Support nested keys with dot notation
        if '.' in key:
            keys = key.split('.')
            value = self._config
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            return value if value is not None else default
        
        return self._config.get(key, default)
    
    def get_env_name(self) -> str:
        """
        Get current environment name
        
        Returns:
            Environment name string
        """
        return self._get_env_name()
    
    @staticmethod
    def substitute_env_vars(value):
        """
        Substitute environment variables in string or dict values
        
        Supports ${VAR_NAME} and ${VAR_NAME:default} syntax for environment variable substitution
        
        Args:
            value: String or dict to process
        
        Returns:
            Processed value with environment variables substituted
        
        Example:
            substitute_env_vars("${HOME}/data") -> "/home/user/data"
            substitute_env_vars("${MISSING_VAR:default}") -> "default"
        """
        if isinstance(value, dict):
            return {k: ConfigManager.substitute_env_vars(v) for k, v in value.items()}
        
        if not value or not isinstance(value, str):
            return value
        
        import re
        # Pattern supports ${VAR} or ${VAR:default}
        pattern = r'\$\{([^:}]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ''
            return os.environ.get(var_name, default_value)
        
        value = re.sub(pattern, replace_var, value)
        return value
    
    def clear_cache(self):
        """Clear cached configuration (forces reload on next access)"""
        self._config = None
        self._env_name = None
        logger.info("Configuration cache cleared")


# Global singleton instance
_config_manager = ConfigManager()


def get_config(reload: bool = False) -> Dict:
    """
    Get configuration dictionary (convenience function)
    
    Args:
        reload: Force reload from file
    
    Returns:
        Configuration dictionary
    
    Example:
        from framework.common.config_manager import get_config
        config = get_config()
        api_url = config.get('api_base_url')
    """
    return _config_manager.get_config(reload)


def get_config_value(key: str, default=None):
    """
    Get a specific configuration value (convenience function)
    
    Args:
        key: Configuration key
        default: Default value if not found
    
    Returns:
        Configuration value
    
    Example:
        from framework.common.config_manager import get_config_value
        api_url = get_config_value('api_base_url')
    """
    return _config_manager.get(key, default)


def get_env_name() -> str:
    """
    Get environment name (convenience function)
    
    Returns:
        Environment name string
    
    Example:
        from framework.common.config_manager import get_env_name
        env = get_env_name()  # Returns 'T12', 'T10', etc.
    """
    return _config_manager.get_env_name()


def substitute_env_vars(value):
    """
    Substitute environment variables (convenience function)
    
    Args:
        value: String or dict to process
    
    Returns:
        Processed value
    
    Example:
        from framework.common.config_manager import substitute_env_vars
        path = substitute_env_vars("${HOME}/data")
    """
    return ConfigManager.substitute_env_vars(value)
