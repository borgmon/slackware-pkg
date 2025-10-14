"""Configuration loader for package definitions."""

import json
import sys
from typing import List

from .models import Package


class ConfigLoader:
    """Loads package configuration from JSON file"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.output_path = None
        self.temp_path = None

    def load_packages(self) -> List[Package]:
        """Load package definitions from JSON file"""
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)

                # Load global paths
                self.output_path = data.get("output_path", "./output")
                self.temp_path = data.get("temp_path", "./tmp")

                # Load packages
                packages_data = data.get("packages", [])
                packages = [Package.from_dict(pkg) for pkg in packages_data]

            print(f"✓ Loaded {len(packages)} package(s) from {self.config_file}")
            return packages

        except FileNotFoundError:
            print(f"✗ Error: Config file '{self.config_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in config file: {e}")
            sys.exit(1)
        except KeyError as e:
            print(f"✗ Error: Missing required field in config: {e}")
            sys.exit(1)
