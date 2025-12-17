#!/usr/bin/env python3
"""
Check Vercel deployment status and diagnose issues using Vercel API
Requires VERCEL_TOKEN environment variable
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional

class VercelAPIClient:
    """Client for Vercel REST API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('VERCEL_TOKEN')
        if not self.token:
            raise ValueError(
                "VERCEL_TOKEN not found. Get one from: https://vercel.com/account/tokens\n"
                "Then set: export VERCEL_TOKEN=your_token"
            )
        
        self.base_url = "https://api.vercel.com"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        try:
            response = requests.get(
                f"{self.base_url}/v9/projects",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('projects', [])
        except Exception as e:
            print(f"❌ Error fetching projects: {e}")
            return []
    
    def get_project(self, project_name: str) -> Optional[Dict]:
        """Get project by name"""
        projects = self.get_projects()
        for project in projects:
            if project.get('name') == project_name:
                return project
        return None
    
    def get_deployments(self, project_id: str, limit: int = 10) -> List[Dict]:
        """Get recent deployments for a project"""
        try:
            response = requests.get(
                f"{self.base_url}/v6/deployments",
                headers=self.headers,
                params={'projectId': project_id, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('deployments', [])
        except Exception as e:
            print(f"❌ Error fetching deployments: {e}")
            return []
    
    def get_deployment(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment details"""
        try:
            response = requests.get(
                f"{self.base_url}/v13/deployments/{deployment_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching deployment: {e}")
            return None
    
    def get_deployment_events(self, deployment_id: str) -> List[Dict]:
        """Get build events/logs for a deployment"""
        try:
            # Try streaming endpoint first
            response = requests.get(
                f"{self.base_url}/v2/deployments/{deployment_id}/events",
                headers=self.headers,
                timeout=30,
                stream=True
            )
            response.raise_for_status()
            
            # Parse streaming response
            events = []
            for line in response.iter_lines():
                if line:
                    try:
                        # Vercel events are newline-delimited JSON
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        # Some lines might not be JSON
                        continue
            return events
        except Exception as e:
            # Try alternative endpoint
            try:
                response = requests.get(
                    f"{self.base_url}/v13/deployments/{deployment_id}/events",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                # Handle different response formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'events' in data:
                    return data['events']
                return []
            except Exception as e2:
                print(f"❌ Error fetching deployment events: {e} (also tried alternative: {e2})")
                return []
    
    def get_function_logs(self, deployment_id: str, function_id: str = None) -> List[Dict]:
        """Get function logs"""
        try:
            url = f"{self.base_url}/v1/deployments/{deployment_id}/logs"
            params = {}
            if function_id:
                params['functionId'] = function_id
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching function logs: {e}")
            return []
    
    def diagnose_project(self, project_name: str = "dentaltrawler"):
        """Comprehensive diagnosis of a project"""
        print(f"\n{'='*60}")
        print(f"🔍 Diagnosing Vercel Project: {project_name}")
        print(f"{'='*60}\n")
        
        # Get project
        project = self.get_project(project_name)
        if not project:
            print(f"❌ Project '{project_name}' not found!")
            print("\nAvailable projects:")
            projects = self.get_projects()
            for p in projects:
                print(f"  - {p.get('name')} ({p.get('id')})")
            return
        
        print(f"✅ Project found: {project.get('name')}")
        print(f"   ID: {project.get('id')}")
        print(f"   URL: {project.get('link', {}).get('production', {}).get('domain', 'N/A')}")
        print()
        
        # Get deployments
        deployments = self.get_deployments(project.get('id'), limit=5)
        if not deployments:
            print("⚠️  No deployments found")
            return
        
        print(f"📦 Recent Deployments ({len(deployments)}):")
        print()
        
        for i, deployment in enumerate(deployments, 1):
            deployment_id = deployment.get('uid')
            state = deployment.get('readyState', 'UNKNOWN')
            created = deployment.get('createdAt', '')
            url = deployment.get('url', 'N/A')
            
            # Status emoji
            status_emoji = {
                'READY': '✅',
                'BUILDING': '🔨',
                'ERROR': '❌',
                'QUEUED': '⏳',
                'CANCELED': '🚫',
                'INITIALIZING': '🔄'
            }.get(state, '❓')
            
            print(f"{i}. {status_emoji} {state}")
            print(f"   ID: {deployment_id}")
            print(f"   URL: {url}")
            print(f"   Created: {created}")
            
            # Get detailed deployment info
            details = self.get_deployment(deployment_id)
            if details:
                # Check for errors
                if state == 'ERROR':
                    print(f"   ⚠️  ERROR STATE - Checking logs...")
                    events = self.get_deployment_events(deployment_id)
                    if events:
                        error_events = [e for e in events if e.get('type') == 'command' and 'error' in str(e).lower()]
                        if error_events:
                            print(f"   ❌ Found {len(error_events)} error events")
                            for event in error_events[:3]:  # Show first 3
                                print(f"      - {event.get('payload', {}).get('text', '')[:100]}")
                
                # Check build info
                build_info = details.get('build', {})
                if build_info:
                    print(f"   Build: {build_info.get('env', 'N/A')}")
            
            print()
        
        # Check latest deployment in detail
        if deployments:
            latest = deployments[0]
            latest_id = latest.get('uid')
            print(f"\n{'='*60}")
            print(f"📋 Latest Deployment Details")
            print(f"{'='*60}\n")
            
            details = self.get_deployment(latest_id)
            if details:
                print(f"State: {details.get('readyState')}")
                print(f"URL: {details.get('url')}")
                print(f"Created: {details.get('createdAt')}")
                
                # Check functions
                functions = details.get('functions', [])
                if functions:
                    print(f"\n🔧 Functions ({len(functions)}):")
                    for func in functions:
                        print(f"  - {func.get('name', 'unknown')}")
                
                # Get build logs
                print(f"\n📝 Build Events:")
                events = self.get_deployment_events(latest_id)
                if events:
                    # Filter important events
                    important = [e for e in events if e.get('type') in ['command', 'stdout', 'stderr']]
                    for event in important[-20:]:  # Last 20 events
                        payload = event.get('payload', {})
                        text = payload.get('text', '')
                        if text:
                            # Truncate long lines
                            if len(text) > 150:
                                text = text[:147] + "..."
                            print(f"  {text}")
                else:
                    print("  (No events found)")
            
            # Check function logs
            print(f"\n📊 Function Logs:")
            logs = self.get_function_logs(latest_id)
            if logs:
                for log_entry in logs[-10:]:  # Last 10 log entries
                    print(f"  {log_entry}")
            else:
                print("  (No function logs found)")
        
        print(f"\n{'='*60}")
        print("✅ Diagnosis complete!")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check Vercel deployment status')
    parser.add_argument('--project', '-p', default='dentaltrawler', help='Project name')
    parser.add_argument('--token', '-t', help='Vercel token (or set VERCEL_TOKEN env var)')
    
    args = parser.parse_args()
    
    try:
        client = VercelAPIClient(token=args.token)
        client.diagnose_project(args.project)
    except ValueError as e:
        print(f"\n❌ {e}\n")
        print("To get a Vercel token:")
        print("1. Go to https://vercel.com/account/tokens")
        print("2. Create a new token")
        print("3. Set: export VERCEL_TOKEN=your_token")
        print("4. Or pass with: --token your_token")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

