"""Slackware Package Builder - Build packages from source into Slackware format."""

from slackware_pkg.builder import SlackwarePackageBuilder
from slackware_pkg.models import BuildConfig, Package

__version__ = "0.1.0"
__all__ = ["SlackwarePackageBuilder", "Package", "BuildConfig"]
