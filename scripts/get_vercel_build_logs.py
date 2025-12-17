#!/usr/bin/env python3
"""
Get detailed build logs for a specific Vercel deployment
"""

import os
import sys
import json
import requests
from typing import Optional

def get_build_logs(deployment_id: str, token: Optional[str] = None):
    """Get build logs for a deployment"""
    token = token or os.getenv('VERCEL_TOKEN')
    if not token:
        print("❌ VERCEL_TOKEN not found")
        sys.exit(1)
    
    base_url = "https://api.vercel.com"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 Fetching build logs for deployment: {deployment_id}\n")
    
    # Try multiple endpoints
    endpoints = [
        f"/v2/deployments/{deployment_id}/events",
        f"/v13/deployments/{deployment_id}/events",
        f"/v1/deployments/{deployment_id}/events",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Trying: {endpoint}...")
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=headers,
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                print(f"✅ Success with {endpoint}\n")
                print("="*60)
                print("BUILD LOGS:")
                print("="*60)
                
                # Handle streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            event = json.loads(line)
                            payload = event.get('payload', {})
                            text = payload.get('text', '')
                            if text:
                                print(text)
                        except json.JSONDecodeError:
                            # Print raw line if not JSON
                            print(line.decode('utf-8', errors='ignore'))
                
                return
            else:
                print(f"  Status: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    # If streaming didn't work, try getting deployment details
    try:
        print("\nTrying deployment details endpoint...")
        response = requests.get(
            f"{base_url}/v13/deployments/{deployment_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        deployment = response.json()
        
        print("\n" + "="*60)
        print("DEPLOYMENT DETAILS:")
        print("="*60)
        print(f"State: {deployment.get('readyState')}")
        print(f"URL: {deployment.get('url')}")
        print(f"Created: {deployment.get('createdAt')}")
        
        # Check for error info
        if deployment.get('readyState') == 'ERROR':
            print("\n❌ DEPLOYMENT FAILED")
            print("\nError information:")
            error_info = deployment.get('error', {})
            if error_info:
                print(json.dumps(error_info, indent=2))
            
            # Check build info
            build = deployment.get('build', {})
            if build:
                print(f"\nBuild environment: {build.get('env', 'N/A')}")
        
        # Check routes
        routes = deployment.get('routes', [])
        if routes:
            print(f"\nRoutes ({len(routes)}):")
            for route in routes[:5]:
                print(f"  {route}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_vercel_build_logs.py <deployment_id> [token]")
        print("\nExample:")
        print("  python3 get_vercel_build_logs.py dpl_8yX9Qy3iVSyKspNDwXusSxvjMYdH")
        sys.exit(1)
    
    deployment_id = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None
    
    get_build_logs(deployment_id, token)

