#!/usr/bin/env python3
"""
Slackware Package Builder
Builds packages from source into Slackware package format (.tgz)

Consolidated single-file version
"""

import json
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# Models
# ============================================================================


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


# ============================================================================
# Configuration Loader
# ============================================================================


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


# ============================================================================
# Git Operations
# ============================================================================


class GitRepository:
    """Handles git repository operations"""

    @staticmethod
    def clone_or_update(pkg: Package, work_dir: Path) -> Optional[Path]:
        """Clone the git repository and checkout specified branch"""
        repo_name = pkg.name
        git_url = pkg.git_url
        branch = pkg.branch
        repo_path = work_dir / repo_name

        print(f"  → Cloning {git_url} (branch: {branch})")

        try:
            # Clone the repository
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--branch",
                    branch,
                    "--depth",
                    "1",
                    git_url,
                    str(repo_path),
                ],
                check=True,
                capture_output=True,
            )

            print(f"  ✓ Repository cloned successfully")
            return repo_path

        except subprocess.CalledProcessError as e:
            print(f"✗ Error cloning repository: {e}")
            return None


# ============================================================================
# Builders
# ============================================================================


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


# ============================================================================
# Slackware Packaging
# ============================================================================


class SlackwarePackager:
    """Creates Slackware packages"""

    @staticmethod
    def create_slack_desc(pkg: Package, install_dir: Path) -> None:
        """Create slack-desc file for the package"""
        name = pkg.name
        desc = pkg.description

        install_docs_dir = install_dir / "install"
        install_docs_dir.mkdir(exist_ok=True)

        slack_desc = install_docs_dir / "slack-desc"

        # Format the slack-desc file
        lines = [
            f"# HOW TO EDIT THIS FILE:",
            f'# The "handy ruler" below makes it easier to edit a package description.',
            f"# Line up the first '|' above the ':' following the base package name, and",
            f"# the '|' on the right side marks the last column you can put a character in.",
            f"# You must make exactly 11 lines for the formatting to be correct.  It's also",
            f"# customary to leave one space after the ':'.",
            f"",
            f"{' ' * (len(name) - 1)}|-----handy-ruler------------------------------------------------------|",
        ]

        # Split description into lines of max 60 characters
        desc_lines = []
        words = desc.split()
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= 60:
                current_line += word + " "
            else:
                desc_lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            desc_lines.append(current_line.strip())

        # Add description lines (need 11 total)
        for i in range(11):
            if i < len(desc_lines):
                lines.append(f"{name}: {desc_lines[i]}")
            else:
                lines.append(f"{name}:")

        with open(slack_desc, "w") as f:
            f.write("\n".join(lines) + "\n")

    @staticmethod
    def create_package_archive(
        pkg: Package, install_dir: Path, output_dir: Path, arch: str = "x86_64"
    ) -> Optional[Path]:
        """Create the .tgz package archive"""
        name = pkg.name
        version = pkg.version
        build = pkg.build

        pkg_filename = f"{name}-{version}-{arch}-{build}.tgz"
        output_file = output_dir / pkg_filename

        print(f"  → Creating package archive: {pkg_filename}")

        # Create tar.gz archive
        result = subprocess.run(
            ["tar", "czf", str(output_file), "-C", str(install_dir), "."],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"✗ Failed to create package archive:")
            print(result.stderr)
            return None

        print(f"  ✓ Package created: {output_file}")
        return output_file


# ============================================================================
# Main Package Builder
# ============================================================================


class SlackwarePackageBuilder:
    """Main orchestrator for building Slackware packages"""

    def __init__(
        self,
        config_file: str = "config.json",
        build_root: str = "build",
        tmp_root: str = "tmp",
    ):
        self.config_file = config_file
        self.build_root = Path(build_root)
        self.tmp_root = Path(tmp_root)
        self.packages: List[Package] = []
        self.builders = [RustBuilder()]  # Add more builders here as needed

        # Create directories if they don't exist
        self.build_root.mkdir(parents=True, exist_ok=True)
        self.tmp_root.mkdir(parents=True, exist_ok=True)

    def load_packages(self) -> None:
        """Load package definitions from JSON file"""
        config_loader = ConfigLoader(self.config_file)
        self.packages = config_loader.load_packages()

        # Use config paths if available
        if config_loader.output_path:
            self.build_root = Path(config_loader.output_path)
            self.build_root.mkdir(parents=True, exist_ok=True)

        if config_loader.temp_path:
            self.tmp_root = Path(config_loader.temp_path)
            self.tmp_root.mkdir(parents=True, exist_ok=True)

    def build_package(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        """Build the package from source"""
        name = pkg.name
        print(f"  → Building {name}...")

        # Find appropriate builder
        for builder in self.builders:
            if builder.can_build(repo_path):
                return builder.build(pkg, repo_path, install_dir)

        print(f"✗ No suitable builder found for {name}")
        return False

    def build_all_packages(self) -> None:
        """Build all packages defined in the configuration"""
        if not self.packages:
            print("No packages to build")
            return

        # Filter enabled packages
        enabled_packages = [pkg for pkg in self.packages if pkg.enabled]

        print(f"\n{'=' * 60}")
        print(
            f"Building {len(enabled_packages)} package(s) (out of {len(self.packages)} total)"
        )
        print(f"{'=' * 60}\n")

        for pkg in self.packages:
            name = pkg.name

            # Skip disabled packages
            if not pkg.enabled:
                print(f"\n[{name}]")
                print(f"{'─' * 60}")
                print(f"⊘ Package disabled - skipping build\n")
                continue

            print(f"\n[{name}]")
            print(f"{'─' * 60}")

            # Create output directory following un-get format
            output_dir = self.build_root / "slackware64-current" / name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create temporary working directory
            temp_dir = self.tmp_root / f"{name}-build"
            temp_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Clone repository
                repo_path = GitRepository.clone_or_update(pkg, temp_dir)
                if not repo_path:
                    print(f"✗ Failed to prepare {name}\n")
                    continue

                # Create install staging directory
                install_dir = temp_dir / "install_staging"
                install_dir.mkdir(exist_ok=True)

                # Build the package
                if not self.build_package(pkg, repo_path, install_dir):
                    print(f"✗ Failed to build {name}\n")
                    continue

                # Create slack-desc
                SlackwarePackager.create_slack_desc(pkg, install_dir)

                # Create package archive
                pkg_file = SlackwarePackager.create_package_archive(
                    pkg, install_dir, output_dir
                )
                if not pkg_file:
                    print(f"✗ Failed to create package for {name}\n")
                    continue

                print(f"✓ Successfully built {name}")

            except Exception as e:
                print(f"✗ Error during build: {e}")
            finally:
                # Clean up temp directory after build
                if temp_dir.exists():
                    print(f"  → Cleaning up temporary files...")
                    shutil.rmtree(temp_dir, ignore_errors=True)

        print(f"\n{'=' * 60}")
        print(
            f"Build complete! Packages saved to: {self.build_root / 'slackware64-current'}"
        )
        print(f"{'=' * 60}\n")


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    builder = SlackwarePackageBuilder()
    builder.load_packages()
    builder.build_all_packages()


if __name__ == "__main__":
    print("starting..")
    main()
