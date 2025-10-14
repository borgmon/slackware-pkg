"""Package builders for different build systems."""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from .models import Package


class Builder(ABC):
    """Abstract base class for package builders"""

    @abstractmethod
    def can_build(self, repo_path: Path) -> bool:
        """Check if this builder can handle the package"""
        pass

    @abstractmethod
    def build(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        """Build the package and install to staging directory"""
        pass


class RustBuilder(Builder):
    """Builds Rust packages using Cargo"""

    def can_build(self, repo_path: Path) -> bool:
        """Check if this is a Rust project"""
        return (repo_path / "Cargo.toml").exists()

    def build(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        """Build a Rust package using cargo"""
        name = pkg.name
        print(f"  → Building {name} with Cargo...")

        # Get build configuration
        build_config = pkg.build_config

        # Build cargo command
        cargo_cmd = ["cargo", "build", "--release"]

        # Add custom features if specified
        if build_config.features:
            features_str = ",".join(build_config.features)
            cargo_cmd.extend(["--features", features_str])
            print(f"    → Enabling features: {features_str}")

        # Add custom target if specified
        target = build_config.target
        if target:
            cargo_cmd.extend(["--target", target])
            print(f"    → Building for target: {target}")

        # Add any additional cargo flags
        if build_config.cargo_flags:
            cargo_cmd.extend(build_config.cargo_flags)

        # Set environment variables if specified
        env = os.environ.copy()
        if build_config.env:
            env.update(build_config.env)
            print(
                f"    → Setting environment variables: {', '.join(build_config.env.keys())}"
            )

        # Build with cargo
        print(f"    → Running: {' '.join(cargo_cmd)}")
        result = subprocess.run(
            cargo_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            print(f"✗ Cargo build failed:")
            print(result.stderr)
            return False

        # Install to staging directory
        return self._install_artifacts(pkg, repo_path, install_dir, target)

    def _install_artifacts(
        self, pkg: Package, repo_path: Path, install_dir: Path, target: str = None
    ) -> bool:
        """Install build artifacts to staging directory"""
        print(f"    → Installing to staging directory...")

        # Create directory structure
        bin_dir = install_dir / "usr" / "bin"
        doc_dir = install_dir / "usr" / "doc" / f"{pkg.name}-{pkg.version}"
        bin_dir.mkdir(parents=True, exist_ok=True)
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Determine release directory based on target
        if target:
            release_dir = repo_path / "target" / target / "release"
        else:
            release_dir = repo_path / "target" / "release"

        # Copy binaries
        binaries_installed = False
        for binary_name in pkg.binaries:
            binary_src = release_dir / binary_name
            if binary_src.exists() and binary_src.is_file():
                shutil.copy2(binary_src, bin_dir / binary_name)
                os.chmod(bin_dir / binary_name, 0o755)
                print(f"    ✓ Installed binary: {binary_name}")
                binaries_installed = True
            else:
                print(f"    ⚠ Binary not found: {binary_name}")

        if not binaries_installed:
            print(f"✗ No binaries found in {release_dir}")
            return False

        # Copy documentation
        for doc_file in ["README.md", "LICENSE", "CHANGELOG.md"]:
            src = repo_path / doc_file
            if src.exists():
                shutil.copy2(src, doc_dir / doc_file)

        return True
