# Docker Build Troubleshooting Guide

## GitHub Actions Cache 502 Error

### Problem

You may encounter a 502 Bad Gateway error when GitHub Actions tries to export build cache:

```
ERROR: failed to solve: failed to parse error response 502: <!DOCTYPE html>
```

### Root Causes

1. **GitHub Infrastructure Issues**: Temporary problems with GitHub's cache service
2. **Cache Size Limitations**: Build cache exceeding GitHub's limits
3. **Network Connectivity**: Issues between GitHub runners and cache service
4. **Concurrent Cache Operations**: Multiple builds trying to write cache simultaneously

### Solutions

#### Solution 1: Use Improved CI Workflow (Recommended)

The main CI workflow (`ci.yml`) has been updated with:

- **Fallback mechanism**: If cache fails, builds without cache
- **Reduced cache mode**: Uses `mode=min` instead of `mode=max`
- **Error handling**: `continue-on-error: true` for cache operations
- **Image export**: Saves images to tar files for verification

#### Solution 2: Use No-Cache Workflow

For critical builds, use the alternative workflow:

```bash
# Trigger the no-cache workflow
git push origin main
```

The `ci-no-cache.yml` workflow completely avoids GitHub Actions cache.

#### Solution 3: Manual Docker Build

Build locally without cache:

```bash
# Backend
docker build --no-cache -t lead-to-lease-backend:local ./backend

# Frontend
docker build --no-cache -t lead-to-lease-frontend:local ./frontend

# Fullstack
docker build --no-cache -t lead-to-lease-fullstack:local .
```

### Prevention Strategies

#### 1. Optimize Dockerfile Layers

- Use multi-stage builds
- Copy package files before source code
- Minimize layer size
- Use `.dockerignore` files

#### 2. Cache Configuration

```yaml
# Minimal cache mode (recommended)
cache-to: type=gha,mode=min

# No cache (most reliable)
# Remove cache-from and cache-to entirely
```

#### 3. Build Optimization

```yaml
# Add build arguments to reduce cache size
build-args: |
  BUILDKIT_INLINE_CACHE=1
  BUILDKIT_MULTI_PLATFORM=false
```

### Monitoring and Debugging

#### Check Build Logs

1. Go to GitHub Actions tab
2. Click on the failed workflow
3. Expand the "Build Docker image" step
4. Look for cache-related errors

#### Verify Docker Images

```bash
# List built images
docker images

# Test image functionality
docker run --rm your-image:tag command
```

#### Clear GitHub Actions Cache

```bash
# Using GitHub CLI
gh cache list
gh cache delete <cache-key>
```

### Alternative Solutions

#### Use Docker Registry Cache

Instead of GitHub Actions cache, use a Docker registry:

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: your-registry/image:latest
    cache-from: type=registry,ref=your-registry/image:cache
    cache-to: type=registry,ref=your-registry/image:cache,mode=max
```

#### Use Local Cache

For self-hosted runners:

```yaml
cache-from: type=local,src=/tmp/.buildx-cache
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

### Best Practices

1. **Keep Dockerfiles simple**: Minimize layers and complexity
2. **Use .dockerignore**: Exclude unnecessary files
3. **Regular cache cleanup**: Clear old caches periodically
4. **Monitor build times**: Track performance improvements
5. **Test locally first**: Verify builds work without cache

### Emergency Procedures

If builds consistently fail:

1. **Disable cache temporarily**:

   ```yaml
   # Comment out cache lines
   # cache-from: type=gha
   # cache-to: type=gha,mode=max
   ```

2. **Use alternative workflow**:

   ```bash
   # Rename ci-no-cache.yml to ci.yml temporarily
   mv .github/workflows/ci.yml .github/workflows/ci-with-cache.yml
   mv .github/workflows/ci-no-cache.yml .github/workflows/ci.yml
   ```

3. **Build and deploy manually**:

   ```bash
   docker build -t app:latest .
   docker push your-registry/app:latest
   ```

### Getting Help

- Check [GitHub Status](https://www.githubstatus.com/) for service issues
- Review [Docker Buildx documentation](https://docs.docker.com/buildx/)
- Search [GitHub Actions community](https://github.community/) for similar issues
