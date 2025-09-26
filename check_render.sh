#!/bin/bash

echo "Checking Creative Brief Generator deployment..."
echo "=============================================="

# Render API credentials (same API key, different service)
API_KEY="rnd_U8k5OpYSqJLuiuMGuAG2VKFtujlF"
SERVICE_ID="srv-d3an3n6r433s73dgb2fg"
SERVICE_URL="https://creative-brief-generator.onrender.com"

# Check health endpoint
echo -e "\n📡 Health Check:"
curl -s $SERVICE_URL/health | python3 -m json.tool 2>/dev/null || echo "Service not responding"

# Get service status
echo -e "\n📊 Service Status:"
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://api.render.com/v1/services/$SERVICE_ID" | python3 -m json.tool | grep -E '"status"|"lastDeployedAt"|"name"'

# Get latest deploy info
echo -e "\n🚀 Latest Deploy:"
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1" | python3 -m json.tool | grep -E '"status"|"createdAt"|"finishedAt"|"error"'

echo -e "\n📋 Dashboard Link:"
echo "https://dashboard.render.com/web/$SERVICE_ID/logs"
echo ""
echo "If build failed, look for:"
echo "  - 'ModuleNotFoundError' - Missing dependency"
echo "  - 'Invalid Python version' - Python version issue"
echo "  - 'pip install' errors - Package installation issues"