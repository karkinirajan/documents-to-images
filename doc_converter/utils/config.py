"""
Configuration management utilities.
"""

import copy
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for the document converter.
    """

    DEFAULT_CONFIG = {
        "output": {
            "image_format": "jpeg",
            "image_quality": 95,
            "image_dpi": 200,
            "pdf_quality": "high",
        },
        "conversion": {"batch_size": 10, "timeout": 300, "max_workers": 4},
        "paths": {"temp_dir": "./temp", "output_dir": "./output"},
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "libreoffice": {"timeout": 300, "headless": True},
        "wkhtmltopdf": {
            "page_size": "A4",
            "margin_top": "0.75in",
            "margin_right": "0.75in",
            "margin_bottom": "0.75in",
            "margin_left": "0.75in",
            "encoding": "UTF-8",
        },
    }

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (optional)
        """
        # deep copy: a shallow copy shares the nested dicts, so set()/load would edit the defaults
        self.config_data = copy.deepcopy(self.DEFAULT_CONFIG)

        if config_path:
            self.load_from_file(config_path)

        self._setup_logging()
        logger.info("Configuration initialized")

    def load_from_file(self, config_path: str | Path) -> None:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, encoding="utf-8") as f:
                user_config = yaml.safe_load(f)

            if user_config:
                self._merge_config(self.config_data, user_config)
                logger.info(f"Loaded configuration from: {config_path}")

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise

    def save_to_file(self, config_path: str | Path) -> None:
        """
        Save current configuration to YAML file.

        Args:
            config_path: Path where to save configuration
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to: {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'output.image_format')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value: Any = self.config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'output.image_format')
            value: Value to set
        """
        keys = key.split(".")
        config: Any = self.config_data

        # Navigate to parent of final key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set final value
        config[keys[-1]] = value
        logger.debug(f"Set configuration: {key} = {value}")

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """
        Recursively merge configuration dictionaries.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _setup_logging(self) -> None:
        """
        Setup logging configuration.
        """
        log_level = self.get("logging.level", "INFO")
        log_format = self.get("logging.format")

        # Convert string level to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        logging.basicConfig(
            level=numeric_level,
            format=log_format,
            force=True,  # Override any existing configuration
        )

    def get_output_config(self) -> dict[str, Any]:
        """
        Get output-related configuration.

        Returns:
            Dictionary with output configuration
        """
        result: dict[str, Any] = self.get("output", {})
        return result

    def get_conversion_config(self) -> dict[str, Any]:
        """
        Get conversion-related configuration.

        Returns:
            Dictionary with conversion configuration
        """
        result: dict[str, Any] = self.get("conversion", {})
        return result

    def get_paths_config(self) -> dict[str, Any]:
        """
        Get paths-related configuration.

        Returns:
            Dictionary with paths configuration
        """
        result: dict[str, Any] = self.get("paths", {})
        return result

    def get_libreoffice_config(self) -> dict[str, Any]:
        """
        Get LibreOffice-related configuration.

        Returns:
            Dictionary with LibreOffice configuration
        """
        result: dict[str, Any] = self.get("libreoffice", {})
        return result

    def get_wkhtmltopdf_config(self) -> dict[str, Any]:
        """
        Get wkhtmltopdf-related configuration.

        Returns:
            Dictionary with wkhtmltopdf configuration
        """
        result: dict[str, Any] = self.get("wkhtmltopdf", {})
        return result
