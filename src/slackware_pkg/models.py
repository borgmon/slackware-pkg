"""Data models for package definitions."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Package:
    """Package definition"""

    name: str
    git_url: str
    branch: str
    version: str
    description: str
    build: int = 1
    enabled: bool = True
    release: bool = False
    build_env: Optional[str] = None
    build_command: Optional[str] = None
    bin_path: Optional[str] = None
    only: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        """Create Package from dictionary"""
        return cls(
            name=data["name"],
            git_url=data["git_url"],
            branch=data["branch"],
            version=data["version"],
            description=data.get("description", ""),
            build=data.get("build", 1),
            enabled=data.get("enabled", True),
            release=data.get("release", False),
            build_env=data.get("build_env"),
            build_command=data.get("build_command"),
            bin_path=data.get("bin_path"),
            only=data.get("only", False),
        )
