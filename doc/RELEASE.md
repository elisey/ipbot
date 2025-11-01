# Release Guide

This guide explains how to create and publish new releases of IP Bot.

## Overview

IP Bot uses an automated release process via GitHub Actions. When you push a version tag, the CI/CD pipeline automatically:

1. Builds a Docker image with the new version
2. Publishes it to GitHub Container Registry (ghcr.io)
3. Tags the image with both the semantic version and `latest`

## Pre-Release Checklist

Before creating a release, ensure:

- [ ] All changes are committed and pushed to the `main` branch
- [ ] All tests pass locally (`task check`)
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated (README.md, CONTRIBUTION.md, etc.)
- [ ] CHANGELOG or commit history clearly describes the changes

## Release Process

### Step 1: Update Version Number

Update the version in `pyproject.toml`:

```toml
[project]
name = "ipbot"
version = "0.4.0"  # Update this line
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR version** (1.0.0 → 2.0.0): Breaking changes
- **MINOR version** (0.3.0 → 0.4.0): New features, backwards-compatible
- **PATCH version** (0.3.0 → 0.3.1): Bug fixes, backwards-compatible

Commit the version change:

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.4.0"
git push
```

### Step 2: Create and Push Version Tag

Create an annotated tag with the new version:

```bash
# Create a tag (must match the version in pyproject.toml)
git tag v0.4.0

# Push the tag to trigger the release workflow
git push origin v0.4.0
```

**Important**: The tag format must be `v` followed by the semantic version (e.g., `v0.4.0`, `v1.2.3`).

### Step 3: Monitor the Workflow

The GitHub Actions workflow will automatically start when you push the tag.

1. Visit your repository's Actions page:
   ```
   https://github.com/elisey/ipbot/actions
   ```

2. Look for the "Release - Docker Build and Publish" workflow run

3. The workflow will:
   - Check out your code at the tagged version
   - Build the Docker image using the multi-stage Dockerfile
   - Run any build-time tests
   - Push the image to GitHub Container Registry with two tags:
     - Semantic version tag (e.g., `0.4.0`)
     - `latest` tag

4. Wait for the workflow to complete (usually 2-5 minutes)

### Step 4: Verify the Release

Once the workflow completes successfully:

1. **Check GitHub Container Registry:**
   - Visit: `https://github.com/elisey/ipbot/pkgs/container/ipbot`
   - Verify both tags are present:
     - `ghcr.io/elisey/ipbot:0.4.0`
     - `ghcr.io/elisey/ipbot:latest`

2. **Test the new image:**
   ```bash
   # Pull the new version
   docker pull ghcr.io/elisey/ipbot:0.4.0

   # Or pull latest
   docker pull ghcr.io/elisey/ipbot:latest

   # Test it works
   docker run --env-file .env ghcr.io/elisey/ipbot:0.4.0
   ```

3. **Update deployment:**
   - If you have the bot running in production, update your deployment to use the new version
   - For docker-compose deployments, users can pull the new `latest` tag or specify the version

## Example: Complete Release Workflow

Here's a complete example of releasing version 0.4.0:

```bash
# 1. Ensure you're on main with latest changes
git checkout main
git pull

# 2. Run tests to ensure everything works
task check

# 3. Update version in pyproject.toml
# Edit the file to change version = "0.4.0"

# 4. Commit version bump
git add pyproject.toml
git commit -m "chore: bump version to 0.4.0"

# 5. Push to main
git push

# 6. Create and push tag
git tag v0.4.0
git push origin v0.4.0

# 7. Monitor the workflow at:
# https://github.com/elisey/ipbot/actions

# 8. Verify the release at:
# https://github.com/elisey/ipbot/pkgs/container/ipbot
```

## Troubleshooting

### Workflow Fails to Trigger

**Problem**: You pushed a tag but the workflow didn't start.

**Solution**:
- Verify the tag format is correct (must start with `v`)
- Check that the tag was pushed to the remote:
  ```bash
  git ls-remote --tags origin
  ```

### Docker Build Fails

**Problem**: The workflow starts but the Docker build step fails.

**Solution**:
- Review the workflow logs in the Actions tab
- Test the Docker build locally:
  ```bash
  docker build -f docker/Dockerfile -t ipbot:test .
  ```
- Common issues:
  - Missing dependencies in pyproject.toml
  - Syntax errors in Python code
  - Invalid Dockerfile syntax

### Image Push Fails

**Problem**: Build succeeds but pushing to registry fails.

**Solution**:
- Verify GitHub Actions has permission to push to GHCR
- Check repository settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is enabled

### Wrong Version Tag

**Problem**: You pushed a tag with the wrong version number.

**Solution**:
```bash
# Delete the local tag
git tag -d v0.4.0

# Delete the remote tag
git push origin --delete v0.4.0

# Create the correct tag
git tag v0.4.1
git push origin v0.4.1
```

### Need to Update a Release

**Problem**: You need to fix something in an already-released version.

**Solution**:
- For critical fixes: Create a new patch version (e.g., 0.4.0 → 0.4.1)
- Never reuse or overwrite existing version tags
- Never force-push tags to the remote

## Release Cadence

There's no fixed release schedule. Create releases when:

- A significant new feature is complete
- Important bug fixes are ready
- Security updates are needed
- Documentation improvements are substantial enough to warrant a new version

For minor documentation fixes or typos, consider batching them with other changes rather than creating a new release immediately.

## Related Documentation

- [Contributing Guide](CONTRIBUTION.md) - Development setup and workflow
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [README](../README.md) - Quick start and usage guide
