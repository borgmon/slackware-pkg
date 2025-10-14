"""Slackware package creation utilities."""

import subprocess
from pathlib import Path
from typing import Optional

from .models import Package


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
