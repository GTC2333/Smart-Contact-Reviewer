"""
Configuration manager using singleton pattern.
Provides type-safe access to configuration settings.
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache


class ConfigManager:
    """Singleton configuration manager."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Dict[str, Any]] = None
    _project_root: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._project_root = Path(__file__).parent.parent
            self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML files."""
        config_dir = self._project_root / "config"

        # Load settings.yaml (default configuration)
        settings_path = config_dir / "settings.yaml"
        if not settings_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {settings_path}")

        with open(settings_path, encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        # Load local.yaml (local overrides, not committed to git)
        local_path = config_dir / "local.yaml"
        if local_path.exists():
            with open(local_path, encoding="utf-8") as f:
                local_config = yaml.safe_load(f)
                if local_config:
                    self._merge_config(self._config, local_config)

        # Load prompt templates
        prompts_path = config_dir / "prompt_templates.yaml"
        if prompts_path.exists():
            with open(prompts_path, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)
                if "prompt_templates" not in self._config:
                    self._config["prompt_templates"] = {}
                self._config["prompt_templates"].update(prompts)

    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def reload(self):
        """Reload configuration from files."""
        self._config = None
        self._load_config()
    
    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return self._project_root
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key (e.g., 'agents.contract_formatter.model')."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.get(f"agents.{agent_name}", {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.get("llm", {})
    
    def get_prompt_template(self, template_key: str) -> str:
        """Get prompt template by key."""
        # Try direct access first (if prompt_templates is at root level)
        templates = self._config.get("prompt_templates", {})
        # If not found, try getting from config directly (for backward compatibility)
        if not templates:
            templates = self._config
        template = templates.get(template_key)
        if not template:
            raise ValueError(f"Prompt template '{template_key}' not found. Available keys: {list(templates.keys())}")
        return template
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Get frontend configuration."""
        return self.get("frontend", {})
    
    def get_backend_config(self) -> Dict[str, Any]:
        """Get backend API configuration."""
        return self.get("backend_api", {})


# Global instance
@lru_cache()
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    return ConfigManager()
