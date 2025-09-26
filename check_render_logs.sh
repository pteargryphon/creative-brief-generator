#!/bin/bash
# Script to check Render logs for the creative-brief-generator service

RENDER_API_KEY="rnd_U8k5OpYSqJLuiuMGuAG2VKFtujlF"
SERVICE_ID="srv-d3an3n6r433s73dgb2fg"

echo "Fetching Render service events..."
echo "================================"

# Get recent events
curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/services/$SERVICE_ID/events?limit=5" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data:
    event = item['event']
    print(f\"{event['timestamp']}: {event['type']}\")
    if 'details' in event and 'deployStatus' in event['details']:
        print(f\"  Status: {event['details']['deployStatus']}\")
"

echo ""
echo "Latest deployment info:"
echo "======================="

# Get latest deploy
curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
if data:
    deploy = data[0]['deploy']
    print(f\"Deploy ID: {deploy['id']}\")
    print(f\"Status: {deploy['status']}\")
    print(f\"Commit: {deploy['commit']['message'][:100]}\")
    print(f\"Created: {deploy['createdAt']}\")
"

echo ""
echo "Service URL: https://creative-brief-generator.onrender.com"