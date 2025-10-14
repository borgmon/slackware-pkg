"""Release downloader for pre-built packages."""

import subprocess
from pathlib import Path
from typing import Optional

from slackware_pkg.models import Package


class ReleaseDownloader:
    """Handles downloading official release packages"""

    @staticmethod
    def construct_release_url(pkg: Package) -> str:
        """Construct the release URL from git_url, branch, and name"""
        # Extract owner and repo from git_url
        # Example: https://github.com/zyedidia/micro.git -> zyedidia/micro
        git_url = pkg.git_url.rstrip("/")
        if git_url.endswith(".git"):
            git_url = git_url[:-4]

        # Construct download URL
        # Format: https://github.com/{owner}/{repo}/releases/download/{version}/{name}-{version}-linux64.tgz
        release_url = f"{git_url}/releases/download/{pkg.branch}/{pkg.name}-{pkg.version}-linux64.tgz"
        return release_url

    @staticmethod
    def download_release(
        pkg: Package, output_dir: Path, arch: str = "x86_64"
    ) -> Optional[Path]:
        """Download the official release package directly to output directory"""
        release_url = ReleaseDownloader.construct_release_url(pkg)

        # Create output filename in Slackware format
        pkg_filename = f"{pkg.name}-{pkg.version}-{arch}-{pkg.build}.tgz"
        output_file = output_dir / pkg_filename

        print(f"  → Downloading from {release_url}")

        try:
            # Download using curl
            subprocess.run(
                [
                    "curl",
                    "-L",  # Follow redirects
                    "-o",
                    str(output_file),
                    release_url,
                ],
                check=True,
                capture_output=True,
            )

            print(f"  ✓ Package downloaded: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            print(f"✗ Error downloading release: {e}")
            return None
