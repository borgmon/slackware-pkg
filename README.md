# Slackware Package Builder

A Python tool to build packages from source into Slackware package format (.tgz).

## Packages included

<packages>

</packages>

## Features

- Build packages from source Git repositories
- Generic build system support (Rust, Go, Make, etc.)
- Automatic package versioning
- Follows Slackware package standards
- Enable/disable individual packages
- Download pre-built releases or build from source

## Automated Builds with GitHub Actions

This project uses GitHub Actions to automatically build packages on every push to the `main` branch. The workflow:

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

## Development

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd slackware-pkg

# Sync dependencies (installs the package automatically)
uv sync
```

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

Edit `config.json` to define packages to build. To add a new package, simply add an entry to it.

### Package Configuration Fields

- **name** (required): Package name
- **git_url** (required): Git repository URL
- **tag** (required): Git tag or branch to checkout (used for git clone and release download)
- **description** (required): Package description
- **build** (optional, default: 1): Build number
- **enabled** (optional, default: true): Set to `false` to skip building this package
- **only** (optional, default: false): Set to `true` to build only this package. Useful for testing
- **release** (optional, default: false): Set to `true` to download pre-built release instead of building from source
- **build_env** (optional): Build environment identifier (e.g., "rust", "go", "python") - used for GitHub Actions toolchain installation
- **build_command** (optional): Shell command to build the package (required if not using release)
- **bin_path** (optional): Relative path from repo root to the built binary (required if not using release)

To add a new package, simply add an entry to `config.json`:

```json
{
  "name": "your-package",
  "git_url": "https://github.com/user/repo.git",
  "tag": "v1.0.0",
  "description": "Package description",
  "build": 1,
  "enabled": true,
  "build_env": "rust",
  "build_command": "cargo build --release",
  "bin_path": "target/release/your-package"
}
```

**Version Derivation:**
If the tag starts with `v` (e.g., `v1.2.3`), the version will be the numeric part after `v` (e.g., `1.2.3`). Otherwise, the tag itself is used as the version.

The builder is fully generic and uses the `build_command` you specify. No code changes needed!

### Docker Development

You can use docker to test if a package will be built successfully before push to main.

```bash
docker compose up -d
```
