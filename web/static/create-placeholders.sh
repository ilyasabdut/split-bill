#!/bin/bash

# Create minimal placeholder PNG files for PWA
# These are base64 encoded 1x1 transparent PNGs that will be replaced with actual icons

echo "Creating placeholder PWA icons..."

# 192x192 placeholder (base64 encoded transparent 1x1 PNG)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > icon-192.png

# 512x512 placeholder
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > icon-512.png

echo "Placeholder icons created. Replace with actual icons when available."
