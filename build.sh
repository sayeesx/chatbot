#!/usr/bin/env bash
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install Python packages from requirements.txt
pip install --no-cache-dir -r requirements.txt
