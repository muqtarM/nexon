#!/usr/bin/env bash

# Demo script: full Nexon workflow
set -e

echo "[1/7] Creating environment 'demo' with role animator"
nexon create-env demo --role animator

echo "\n[2/7] Scaffolding package 'mytool' version 0.1.0"
nexon create-package mytool 0.1.0

echo "\n[3/7] Installing 'mytool' into 'demo' (with dependency resolution)"
nexon install-package demo mytool

echo "\n[4/7] Listing environments and packages"
nexon list-envs
nexon list-packages

echo "\n[5/7] Activating 'demo' environment"
nexon activate-env demo

echo "\nActive environment variables:"
env | grep NEXON_ENV || true

echo "\n[6/7] Locking environment 'demo' for reproducibility"
nexon lock-env demo

echo "\n[7/7] Building Docker image for 'demo'"
nexon build-docker demo --tag myorg/demo:1.0

echo "\n✅ Nexon demo complete!"
