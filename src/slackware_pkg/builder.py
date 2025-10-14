"""Main package builder orchestrator."""

import shutil
from pathlib import Path
from typing import List

from slackware_pkg.builders import Builder, GenericBuilder
from slackware_pkg.config import ConfigLoader
from slackware_pkg.git import GitRepository
from slackware_pkg.models import Package
from slackware_pkg.packager import SlackwarePackager
from slackware_pkg.release import ReleaseDownloader


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
        self.builders: List[Builder] = [
            GenericBuilder()
        ]  # Generic builder that uses build_command from config

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
            if builder.can_build(pkg, repo_path):
                return builder.build(pkg, repo_path, install_dir)

        print(f"✗ No suitable builder found for {name}")
        return False

    def build_single_package_direct(self, pkg: Package) -> bool:
        """Build a single package directly without loading from config"""
        name = pkg.name

        print(f"\n[{name}]")
        print(f"{'─' * 60}")

        # Create output directory following un-get format
        output_dir = self.build_root / "slackware64-current" / name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check if this is a release package (download directly)
        if pkg.release:
            print(f"  → Package has official release - downloading directly")

            try:
                # Download the release directly to output directory
                pkg_file = ReleaseDownloader.download_release(pkg, output_dir)
                if not pkg_file:
                    print(f"✗ Failed to download release for {name}\n")
                    return False

                print(f"✓ Successfully downloaded {name}")
                return True

            except Exception as e:
                print(f"✗ Error during download: {e}")
                return False

        # Build from source (existing behavior)
        print(f"  → Building from source")

        # Create temporary working directory
        temp_dir = self.tmp_root / f"{name}-build"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Clone repository
            repo_path = GitRepository.clone_or_update(pkg, temp_dir)
            if not repo_path:
                print(f"✗ Failed to prepare {name}\n")
                return False

            # Create install staging directory
            install_dir = temp_dir / "install_staging"
            install_dir.mkdir(exist_ok=True)

            # Build the package
            if not self.build_package(pkg, repo_path, install_dir):
                print(f"✗ Failed to build {name}\n")
                return False

            # Create slack-desc
            SlackwarePackager.create_slack_desc(pkg, install_dir)

            # Create package archive
            pkg_file = SlackwarePackager.create_package_archive(
                pkg, install_dir, output_dir
            )
            if not pkg_file:
                print(f"✗ Failed to create package for {name}\n")
                return False

            print(f"✓ Successfully built {name}")
            return True

        except Exception as e:
            print(f"✗ Error during build: {e}")
            return False
        finally:
            # Clean up temp directory after build
            if temp_dir.exists():
                print(f"  → Cleaning up temporary files...")
                shutil.rmtree(temp_dir, ignore_errors=True)

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

            # Use the single package build method
            self.build_single_package_direct(pkg)

        print(f"\n{'=' * 60}")
        print(
            f"Build complete! Packages saved to: {self.build_root / 'slackware64-current'}"
        )
        print(f"{'=' * 60}\n")
