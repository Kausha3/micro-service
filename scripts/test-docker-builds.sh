#!/bin/bash

# Docker Build Test Script
# This script tests all Docker builds locally to verify they work before pushing to GitHub

set -e  # Exit on any error

echo "🐳 Testing Docker Builds Locally"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to build and test a Docker image
build_and_test() {
    local context=$1
    local dockerfile=$2
    local tag=$3
    local test_command=$4

    echo ""
    echo "Building $tag..."
    echo "Context: $context"
    echo "Dockerfile: $dockerfile"

    # Build the image
    if docker build -t "$tag" -f "$dockerfile" "$context"; then
        print_status "Successfully built $tag"

        # Test the image if test command provided
        if [ -n "$test_command" ]; then
            echo "Testing $tag..."
            if eval "$test_command"; then
                print_status "Successfully tested $tag"
            else
                print_error "Test failed for $tag"
                return 1
            fi
        fi
    else
        print_error "Failed to build $tag"
        return 1
    fi
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Clean up any existing test images
echo ""
echo "Cleaning up existing test images..."
docker rmi lead-to-lease-backend:test 2>/dev/null || true
docker rmi lead-to-lease-frontend:test 2>/dev/null || true
docker rmi lead-to-lease-fullstack:test 2>/dev/null || true

# Build backend
echo ""
echo "🔧 Building Backend Image"
echo "========================="
build_and_test "./backend" "./backend/Dockerfile" "lead-to-lease-backend:test" \
    "docker run --rm lead-to-lease-backend:test python --version"

# Build frontend
echo ""
echo "🎨 Building Frontend Image"
echo "=========================="
build_and_test "./frontend" "./frontend/Dockerfile" "lead-to-lease-frontend:test" \
    "docker run --rm lead-to-lease-frontend:test nginx -v"

# Build fullstack (if Dockerfile exists)
if [ -f "./Dockerfile.fullstack" ]; then
    echo ""
    echo "📦 Building Fullstack Image"
    echo "==========================="
    build_and_test "." "./Dockerfile.fullstack" "lead-to-lease-fullstack:test" ""
else
    print_warning "Dockerfile.fullstack not found, skipping fullstack build"
fi

# Test Docker Compose
echo ""
echo "🐙 Testing Docker Compose"
echo "========================="
if [ -f "docker-compose.yml" ]; then
    if docker compose config > /dev/null 2>&1; then
        print_status "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration is invalid"
        exit 1
    fi
else
    print_warning "docker-compose.yml not found, skipping compose test"
fi

# Show final results
echo ""
echo "📊 Build Summary"
echo "================"
docker images | grep "lead-to-lease" || print_warning "No lead-to-lease images found"

echo ""
print_status "All Docker builds completed successfully!"
echo ""
echo "💡 Tips:"
echo "  - Images are tagged with ':test' suffix"
echo "  - Run 'docker images' to see all built images"
echo "  - Run 'docker rmi <image>' to remove test images"
echo "  - Use 'docker run --rm <image>' to test images"
echo ""
echo "🚀 Ready to push to GitHub!"
