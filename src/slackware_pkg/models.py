"""Data models for package definitions and build configuration."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BuildConfig:
    """Build configuration options"""

    features: List[str] = None
    target: Optional[str] = None
    cargo_flags: List[str] = None
    env: Dict[str, str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.cargo_flags is None:
            self.cargo_flags = []
        if self.env is None:
            self.env = {}


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
    binaries: List[str] = None
    build_config: BuildConfig = None

    def __post_init__(self):
        if self.binaries is None:
            self.binaries = [self.name]
        if self.build_config is None:
            self.build_config = BuildConfig()
        elif isinstance(self.build_config, dict):
            self.build_config = BuildConfig(**self.build_config)

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        """Create Package from dictionary"""
        build_config = data.get("build_config")
        if build_config:
            build_config = BuildConfig(**build_config)

        return cls(
            name=data["name"],
            git_url=data["git_url"],
            branch=data["branch"],
            version=data["version"],
            description=data.get("description", ""),
            build=data.get("build", 1),
            enabled=data.get("enabled", True),
            binaries=data.get("binaries"),
            build_config=build_config,
        )
