# Slackware Package Builder

A Python tool to build packages from source into Slackware package format (.tgz).

## Features

- Build packages from Git repositories
- Support for Rust/Cargo-based projects
- Configurable build options
- Automatic package versioning
- Follows Slackware package standards
- Enable/disable individual packages
- Modular architecture for easy extensibility

## Automated Builds with GitHub Actions

This project uses GitHub Actions to automatically build packages on every push to the `main` branch. The workflow:

1. **Prepares build matrix** - Parses `config.json` and identifies all enabled packages
2. **Builds packages in parallel** - Each package is built in a separate job
   - Skips packages that are already built (checks version in build branch)
   - Uploads built packages as artifacts
3. **Summary step** - After all builds complete:
   - Downloads all package artifacts
   - Copies packages to `slackware64-current/` directory structure
   - Runs `buildlist.sh` to generate `FILE_LIST` and `CHECKSUMS.md5`
   - Commits everything to the `build` branch

All built packages are available in the `build` branch under `slackware64-current/<package-name>/`.

## Usage(un-get)

### Quick

Copy this to your console:

```sh
echo "https://raw.githubusercontent.com/borgmon/slackware-pkg/build/slackware64-current/ borgmon" >> /boot/config/plugins/un-get/sources.list
```

### Manual

Add this to your `/boot/config/plugins/un-get/sources.list`

```
https://raw.githubusercontent.com/borgmon/slackware-pkg/build/slackware64-current/ borgmon
```

## Project Structure

```
slackware-pkg/
├── src/
│   └── slackware_pkg/        # Main package directory
│       ├── __init__.py       # Package exports
│       ├── main.py           # CLI entry point with argument parsing
│       ├── models.py         # Data models (Package, BuildConfig)
│       ├── config.py         # Configuration loader
│       ├── git.py            # Git operations
│       ├── builders.py       # Build system implementations (RustBuilder, etc.)
│       ├── packager.py       # Slackware package creation
│       ├── release.py        # Release downloader for pre-built packages
│       └── builder.py        # Main orchestrator
├── config.json               # Package definitions
├── pyproject.toml            # Project metadata and dependencies
├── uv.lock                   # uv lockfile
├── main.py                   # Legacy wrapper (deprecated)
├── Dockerfile                # Container image definition
└── README.md                 # This file
```

## Requirements

- Python 3.10+
- Git
- Cargo/Rust (for Rust projects)
- Standard build tools (tar, etc.)

## Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd slackware-pkg

# Sync dependencies (installs the package automatically)
uv sync
```

### Using pip

```bash
git clone <repository-url>
cd slackware-pkg
pip install -e .
```

### Using Docker

```bash
# Build the Docker image
docker build -t slackware-pkg .

# Run the builder
docker run -v $(pwd)/config.json:/app/config.json \
           -v $(pwd)/output:/app/output \
           slackware-pkg
```

## Usage

### Command Line

```bash
# Build all enabled packages from config.json
uv run slackware-pkg

# Build a specific package by name
uv run slackware-pkg --package lsd

# Use a custom config file
uv run slackware-pkg --config my-config.json --package ripgrep

# Customize output and temp directories
uv run slackware-pkg --package yazi --output ./build --temp ./tmp

# Show help
uv run slackware-pkg --help
```

### CLI Options

- `--config CONFIG` - Path to config.json file (default: config.json)
- `--package PACKAGE` - Package name to build (if not specified, builds all enabled packages)
- `--output OUTPUT` - Output directory for built packages (default: ./build)
- `--temp TEMP` - Temporary directory for build files (default: ./tmp)

### Configuration

Edit `config.json` to define packages to build:

```json
{
  "output_path": "./output",
  "temp_path": "./tmp",
  "packages": [
    {
      "name": "ripgrep",
      "git_url": "https://github.com/BurntSushi/ripgrep.git",
      "branch": "14.1.1",
      "version": "14.1.1",
      "description": "A line-oriented search tool",
      "build": 1,
      "enabled": true,
      "binaries": ["rg"],
      "build_config": {
        "features": ["pcre2"],
        "target": null,
        "cargo_flags": [],
        "env": {}
      }
    }
  ]
}
```

### Package Configuration Fields

- **name** (required): Package name
- **git_url** (required): Git repository URL
- **branch** (required): Git branch/tag to checkout (used only for git clone operations)
- **version** (required): Package version (used for package naming and documentation paths)
- **description** (required): Package description
- **build** (optional, default: 1): Build number
- **enabled** (optional, default: true): Set to `false` to skip building this package
- **release** (optional, default: false): Set to `true` to download pre-built release instead of building from source
- **binaries** (optional, default: [name]): List of binary names to install
- **build_config** (optional): Build-specific configuration (only for building from source)
  - **features**: Cargo features to enable (list of strings)
  - **target**: Build target architecture (string or null)
  - **cargo_flags**: Additional cargo flags (list of strings)
  - **env**: Environment variables for build (dict)

### Release Downloads

For packages with official pre-built releases (like `micro`), you can set `"release": true` to download the release directly instead of building from source:

```json
{
  "name": "micro",
  "git_url": "https://github.com/zyedidia/micro.git",
  "branch": "v2.0.14",
  "version": "2.0.14",
  "description": "A modern and intuitive terminal-based text editor.",
  "build": 1,
  "enabled": true,
  "release": true
}
```

This will download from: `https://github.com/zyedidia/micro/releases/download/v2.0.14/micro-2.0.14-linux64.tgz`

## Output Structure

Packages are saved to:

```
output/slackware64-current/<package-name>/<package-name>-<version>-<arch>-<build>.tgz
```

## Development

### Running with uv

```bash
# Install development dependencies
uv sync

# Lint code
uv run ruff check src/

# Format code (if ruff format is configured)
uv run ruff format src/

# Run the builder
uv run slackware-pkg

# Run with Python directly
uv run python -m slackware_pkg.main --help
```

### Adding New Build Systems

To add support for new build systems (e.g., Make, CMake, Python setuptools):

1. Create a new builder class in `src/slackware_pkg/builders.py` that inherits from `Builder`
2. Implement the `can_build()` and `build()` methods
3. Register the builder in `SlackwarePackageBuilder.__init__()` in `builder.py`

Example:

```python
class MakeBuilder(Builder):
    def can_build(self, repo_path: Path) -> bool:
        return (repo_path / "Makefile").exists()

    def build(self, pkg: Package, repo_path: Path, install_dir: Path) -> bool:
        # Implementation here
        pass
```

## Docker Development

```bash
# Build the image
docker build -t slackware-pkg .

# Run interactively
docker run -it --entrypoint bash slackware-pkg

# Mount local config and output
docker run -v $(pwd)/config.json:/app/config.json \
           -v $(pwd)/output:/app/output \
           slackware-pkg
```

## License

MIT
