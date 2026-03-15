#!/bin/bash
# Start Lightpanda CDP server for MCP/Playwright integration

# Disable telemetry
export LIGHTPANDA_DISABLE_TELEMETRY=true

echo "Starting Lightpanda CDP server on ws://127.0.0.1:9222..."
echo "Press Ctrl+C to stop"

# Use npx to run Lightpanda
npx @lightpanda/browser serve \
  --host 127.0.0.1 \
  --port 9222 \
  --log_format pretty \
  --log_level info \
  --obey_robots
