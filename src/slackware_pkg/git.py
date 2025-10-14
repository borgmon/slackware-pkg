"""Git repository operations."""

import subprocess
from pathlib import Path
from typing import Optional

from slackware_pkg.models import Package


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
