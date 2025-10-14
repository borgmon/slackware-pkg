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

## Project Structure

```
slackware-pkg/
├── src/
│   └── slackware_pkg/
│       ├── __init__.py       # Package exports
│       ├── __main__.py       # Entry point
│       ├── models.py         # Data models (Package, BuildConfig)
│       ├── config.py         # Configuration loader
│       ├── git.py            # Git operations
│       ├── builders.py       # Build system implementations (RustBuilder, etc.)
│       ├── packager.py       # Slackware package creation
│       └── builder.py        # Main orchestrator
├── config.json               # Package definitions
├── pyproject.toml           # Project metadata and dependencies
├── Dockerfile               # Container image definition
└── README.md                # This file
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

# Install the package
uv pip install -e .
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
python main.py

# Build a specific package by name
python main.py --package lsd

# Use a custom config file
python main.py --config my-config.json --package ripgrep

# Customize output directory (default: ./build)
python main.py --package yazi --output ./
```

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
- **binaries** (optional, default: [name]): List of binary names to install
- **build_config** (optional): Build-specific configuration
  - **features**: Cargo features to enable (list of strings)
  - **target**: Build target architecture (string or null)
  - **cargo_flags**: Additional cargo flags (list of strings)
  - **env**: Environment variables for build (dict)

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

# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Run the builder
uv run slackware-pkg
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
