"""Main entry point for the Slackware Package Builder."""

from .builder import SlackwarePackageBuilder


def main():
    """Main function to build all packages."""
    print("Starting Slackware Package Builder...")
    builder = SlackwarePackageBuilder()
    builder.load_packages()
    builder.build_all_packages()


if __name__ == "__main__":
    main()
