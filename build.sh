#!/usr/bin/env bash
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y python3-dev gcc

# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install --no-cache-dir -r requirements.txt