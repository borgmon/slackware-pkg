"""Main entry point for the Slackware Package Builder."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from slackware_pkg.builder import SlackwarePackageBuilder
from slackware_pkg.models import Package


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Build Slackware packages from source")

    # Main arguments
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to config.json file (default: config.json)",
    )

    parser.add_argument(
        "--package",
        type=str,
        help="Package name to build (if not specified, builds all enabled packages)",
    )

    # Output configuration
    parser.add_argument(
        "--output",
        type=str,
        default="./build",
        help="Output directory for built packages (default: ./build)",
    )
    parser.add_argument(
        "--temp",
        type=str,
        default="./tmp",
        help="Temporary directory for build files (default: ./tmp)",
    )

    return parser.parse_args()


def find_package_in_config(config_file: str, package_name: str) -> Optional[Package]:
    """Find a package by name in the config file"""
    try:
        with open(config_file, "r") as f:
            data = json.load(f)
            packages_data = data.get("packages", [])

            for pkg_data in packages_data:
                if pkg_data.get("name") == package_name:
                    return Package.from_dict(pkg_data)

            return None
    except FileNotFoundError:
        print(f"✗ Error: Config file '{config_file}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in config file: {e}")
        return None


def main():
    """Main function to build packages."""
    args = parse_args()

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"✗ Error: Config file '{args.config}' not found")
        sys.exit(1)

    if args.package:
        # Single package mode - build one package from config
        pkg = find_package_in_config(args.config, args.package)

        if not pkg:
            print(f"✗ Error: Package '{args.package}' not found in {args.config}")
            sys.exit(1)

        # Create builder
        builder = SlackwarePackageBuilder(
            config_file=None,
            build_root=args.output,
            tmp_root=args.temp,
        )

        # Build the single package
        print(f"\n{'=' * 60}")
        print(f"Building package: {args.package}")
        print(f"{'=' * 60}\n")

        success = builder.build_single_package_direct(pkg)

        if success:
            print(f"\n{'=' * 60}")
            print(
                f"✓ Build complete! Package saved to: {Path(args.output) / 'slackware64-current' / args.package}"
            )
            print(f"{'=' * 60}\n")
        else:
            print(f"\n{'=' * 60}")
            print(f"✗ Build failed for {args.package}")
            print(f"{'=' * 60}\n")

        sys.exit(0 if success else 1)
    else:
        # Build all enabled packages from config
        print("Starting Slackware Package Builder...")
        builder = SlackwarePackageBuilder(
            config_file=args.config,
            build_root=args.output,
            tmp_root=args.temp,
        )
        builder.load_packages()
        builder.build_all_packages()


if __name__ == "__main__":
    main()
