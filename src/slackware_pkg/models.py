"""Data models for package definitions."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass

class Package:
    """Package definition"""

    def __init__(
        self,
        name: str,
        git_url: str,
        tag: str,
        description: str,
        build: int = 1,
        enabled: bool = True,
        release: bool = False,
        build_env: Optional[str] = None,
        build_command: Optional[str] = None,
        bin_path: Optional[str] = None,
        only: bool = False,
    ):
        self.name = name
        self.git_url = git_url
        self.tag = tag
        self.description = description
        self.build = build
        self.enabled = enabled
        self.release = release
        self.build_env = build_env
        self.build_command = build_command
        self.bin_path = bin_path
        self.only = only

        # Derive version from tag
        self.version = self._derive_version_from_tag(tag)

    @staticmethod
    def _derive_version_from_tag(tag: str) -> str:
        # If tag starts with 'v' and is like v1.2.3, return 1.2.3
        if tag.startswith("v") and len(tag) > 1 and tag[1].isdigit():
            return tag[1:]
        return tag

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        """Create Package from dictionary"""
        return cls(
            name=data["name"],
            git_url=data["git_url"],
            tag=data["tag"],
            description=data.get("description", ""),
            build=data.get("build", 1),
            enabled=data.get("enabled", True),
            release=data.get("release", False),
            build_env=data.get("build_env"),
            build_command=data.get("build_command"),
            bin_path=data.get("bin_path"),
            only=data.get("only", False),
        )
