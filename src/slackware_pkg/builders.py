"""Package builders for different build systems."""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from slackware_pkg.models import Package


class Builder(ABC):
    """Abstract base class for package builders"""

    @abstractmethod
    def can_build(self, pkg: Package, repo_path: Path) -> bool:
        """Check if this builder can handle the package"""
        pass

    @abstractmethod
    def build(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        """Build the package and install to staging directory"""
        pass


class GenericBuilder(Builder):
    """Generic builder that uses build_command from config"""

    def can_build(self, pkg: Package, repo_path: Path) -> bool:
        """Check if package has a build_command specified"""
        return pkg.build_command is not None

    def build(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        """Build a package using the configured build_command"""
        name = pkg.name
        build_env = pkg.build_env or "unknown"
        print(f"  → Building {name} with {build_env}...")

        # Get build command from config
        build_command = pkg.build_command
        if not build_command:
            print(f"✗ No build_command specified for {name}")
            return False

        # Execute build command
        print(f"    → Running: {build_command}")
        result = subprocess.run(
            build_command,
            shell=True,
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"✗ Build failed:")
            print(result.stderr)
            return False

        print(f"    ✓ Build completed successfully")

        # Install to staging directory
        return self._install_artifacts(pkg, repo_path, install_dir)

    def _install_artifacts(
        self, pkg: Package, repo_path: Path, install_dir: Path
    ) -> bool:
        """Install build artifacts to staging directory"""
        print(f"    → Installing to staging directory...")

        # Create directory structure
        bin_dir = install_dir / "usr" / "bin"
        doc_dir = install_dir / "usr" / "doc" / f"{pkg.name}-{pkg.version}"
        bin_dir.mkdir(parents=True, exist_ok=True)
        doc_dir.mkdir(parents=True, exist_ok=True)

        # bin_path is required - it tells us exactly where the binary is
        if not pkg.bin_path:
            print(f"✗ bin_path not specified in config for {pkg.name}")
            return False

        binary_src = repo_path / pkg.bin_path
        if not binary_src.exists() or not binary_src.is_file():
            print(f"✗ Binary not found at specified path: {pkg.bin_path}")
            return False

        # Use the package name as the installed binary name
        binary_name = pkg.name
        shutil.copy2(binary_src, bin_dir / binary_name)
        os.chmod(bin_dir / binary_name, 0o755)
        print(f"    ✓ Installed binary: {binary_name} (from {pkg.bin_path})")

        # Copy documentation
        for doc_file in ["README.md", "LICENSE", "CHANGELOG.md"]:
            src = repo_path / doc_file
            if src.exists():
                shutil.copy2(src, doc_dir / doc_file)

        return True
