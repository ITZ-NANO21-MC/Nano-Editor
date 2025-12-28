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
            with open(self.env_file, 'r', encoding='utf-8') as f:
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

    def set(self, key, value):
        """Set configuration value and environment variable."""
        self.config[key] = str(value)
        os.environ[key] = str(value)

    def save(self):
        """Save current configuration to .env file."""
        try:
            # Read existing lines to preserve comments
            lines = []
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    lines = f.readlines()
            
            new_lines = []
            keys_written = set()
            
            # Update existing keys
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and '=' in stripped:
                    key = stripped.split('=', 1)[0].strip()
                    if key in self.config:
                        new_lines.append(f"{key}={self.config[key]}\n")
                        keys_written.add(key)
                        continue
                new_lines.append(line)
            
            # Add new keys
            for key, value in self.config.items():
                if key not in keys_written:
                    new_lines.append(f"{key}={value}\n")
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"Error saving .env file: {e}")
            return False


# Global config instance
config = Config()
