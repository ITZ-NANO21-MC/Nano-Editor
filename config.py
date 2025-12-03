"""Configuration management for NanoEditor."""
import os
from pathlib import Path


class Config:
    """Load and manage configuration from .env file."""
    
    def __init__(self):
        self.env_file = Path(__file__).parent / '.env'
        self.config = {}
        self.load_env()
    
    def load_env(self):
        """Load environment variables from .env file."""
        if not self.env_file.exists():
            return
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config[key] = value
                        os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, os.getenv(key, default))
    
    def get_int(self, key, default=0):
        """Get integer configuration value."""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key, default=False):
        """Get boolean configuration value."""
        value = self.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')


# Global config instance
config = Config()
