#!/usr/bin/env python3
"""
Brave Search API helper for OpenClaw
Reads API key from ~/.openclaw/.env
"""

import os
import sys
import urllib.request
import json

# Load API key from .env
env_file = os.path.expanduser("~/.openclaw/.env")
brave_key = None

try:
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('BRAVE_API_KEY='):
                brave_key = line.split('=', 1)[1].strip()
                break
except FileNotFoundError:
    print("Error: .env file not found at ~/.openclaw/.env")
    sys.exit(1)

if not brave_key or brave_key == 'your_brave_search_api_key_here':
    print("Error: BRAVE_API_KEY not set in .env file")
    print("Get API key from: https://brave.com/search/api/")
    sys.exit(1)

# Parse command line arguments
if len(sys.argv) < 2:
    print("Usage: python3 brave_search.py <query> [--results N]")
    sys.exit(1)

query = ' '.join(sys.argv[1:-1]) if sys.argv[-1].startswith('--') else ' '.join(sys.argv[1:])
max_results = 5

# Parse optional --results flag
for arg in sys.argv:
    if arg.startswith('--results='):
        max_results = int(arg.split('=')[1])
    elif arg == '--results' and sys.argv.index(arg) + 1 < len(sys.argv):
        max_results = int(sys.argv[sys.argv.index(arg) + 1])

# Make API request
encoded_query = urllib.parse.quote(query)
url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count={max_results}"

try:
    request = urllib.request.Request(url)
    request.add_header('Accept', 'application/json')
    request.add_header('Accept-Encoding', 'gzip')
    request.add_header('X-Subscription-Token', brave_key)

    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode())

    if 'error' in data:
        print(f"API Error: {data['error']}")
        sys.exit(1)

    # Display results
    print(f"Search results for: {query}\n")

    if 'web' not in data or 'results' not in data['web']:
        print("No results found")
        sys.exit(0)

    for i, result in enumerate(data['web']['results'], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result.get('description', 'No description')}\n")

    print(f"Total: {len(data['web']['results'])} results")

except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"Network Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
