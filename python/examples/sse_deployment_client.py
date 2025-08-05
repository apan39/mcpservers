#!/usr/bin/env python3
"""
Example client for SSE deployment monitoring.
Demonstrates how to use the SSE deployment monitoring tools.
"""

import json
import requests
import time
from typing import Dict, Any

class SSEDeploymentClient:
    """Client for interacting with SSE deployment monitoring."""
    
    def __init__(self, base_url: str = "http://localhost:3009", api_key: str = "4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def start_deployment_with_monitoring(self, app_uuid: str, force: bool = False) -> Dict[str, Any]:
        """Start deployment with SSE monitoring."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "coolify-deploy-with-sse-monitoring",
                "arguments": {
                    "app_uuid": app_uuid,
                    "force": force
                }
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp", json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_deployment_status(self, deployment_uuid: str) -> Dict[str, Any]:
        """Get current deployment status."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "coolify-get-sse-deployment-status",
                "arguments": {
                    "deployment_uuid": deployment_uuid
                }
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp", json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_active_deployments(self) -> Dict[str, Any]:
        """List all active deployments."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "coolify-list-active-sse-deployments",
                "arguments": {}
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp", json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def stream_deployment_updates(self, deployment_uuid: str):
        """Stream real-time deployment updates via SSE."""
        sse_url = f"{self.base_url}/sse/deployment/{deployment_uuid}"
        
        try:
            with requests.get(sse_url, headers=self.headers, stream=True) as response:
                response.raise_for_status()
                
                print(f"🔄 Streaming deployment updates for {deployment_uuid}")
                print("=" * 60)
                
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        
                        if decoded_line.startswith('data: '):
                            data_str = decoded_line[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(data_str)
                                self._handle_sse_event(data)
                                
                                # Break if deployment completed
                                if data.get('type') == 'completed':
                                    print("\n✅ Deployment monitoring completed!")
                                    break
                                    
                            except json.JSONDecodeError:
                                print(f"📝 Raw data: {data_str}")
                        elif decoded_line.startswith('event: '):
                            event_type = decoded_line[7:]  # Remove 'event: ' prefix
                            print(f"🎯 Event: {event_type}")
                            
        except KeyboardInterrupt:
            print("\n⏹️  Stream interrupted by user")
        except Exception as e:
            print(f"❌ Error streaming deployment updates: {e}")
    
    def _handle_sse_event(self, data: Dict[str, Any]):
        """Handle SSE event data."""
        event_type = data.get('type', 'unknown')
        timestamp = data.get('timestamp', '')
        
        if event_type == 'status':
            status = data.get('status', 'unknown')
            print(f"📊 [{timestamp}] Initial Status: {status}")
            
        elif event_type == 'progress':
            status = data.get('status', 'unknown')
            details = data.get('details', {})
            print(f"⏳ [{timestamp}] Progress: {status}")
            if details:
                print(f"   Details: {details}")
                
        elif event_type == 'completed':
            success = data.get('success', False)
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} [{timestamp}] Deployment completed: {'SUCCESS' if success else 'FAILED'}")
            
        elif event_type == 'heartbeat':
            print(f"💓 [{timestamp}] Heartbeat")
            
        elif event_type == 'error':
            message = data.get('message', 'Unknown error')
            print(f"❌ Error: {message}")
            
        else:
            print(f"🔍 [{timestamp}] {event_type}: {data}")

def main():
    """Example usage of SSE deployment monitoring."""
    client = SSEDeploymentClient()
    
    # Example application UUID (replace with actual UUID)
    app_uuid = "zs8sk0cgs4s8gsgwswsg88ko"  # Python MCP server UUID
    
    print("🚀 SSE Deployment Monitoring Example")
    print("=" * 50)
    
    try:
        # 1. List current active deployments
        print("1. Checking active deployments...")
        active_result = client.list_active_deployments()
        if active_result.get('result', {}).get('content'):
            content = active_result['result']['content'][0]['text']
            print(content)
        
        print("\n" + "=" * 50)
        
        # 2. Start deployment with monitoring
        print(f"2. Starting deployment with SSE monitoring for app: {app_uuid}")
        deploy_result = client.start_deployment_with_monitoring(app_uuid, force=True)
        print("Deploy result:", json.dumps(deploy_result, indent=2))
        
        # Extract deployment UUID from result
        content = deploy_result.get('result', {}).get('content', [{}])[0].get('text', '')
        deployment_uuid = None
        
        # Parse deployment UUID from response text
        for line in content.split('\n'):
            if 'Deployment UUID:' in line:
                deployment_uuid = line.split('Deployment UUID:')[1].strip()
                break
        
        if not deployment_uuid:
            print("❌ Could not extract deployment UUID from response")
            return
        
        print(f"📋 Deployment UUID: {deployment_uuid}")
        
        print("\n" + "=" * 50)
        
        # 3. Stream real-time updates
        print("3. Streaming real-time deployment updates...")
        time.sleep(2)  # Brief pause before streaming
        client.stream_deployment_updates(deployment_uuid)
        
        print("\n" + "=" * 50)
        
        # 4. Check final status
        print("4. Checking final deployment status...")
        status_result = client.get_deployment_status(deployment_uuid)
        if status_result.get('result', {}).get('content'):
            content = status_result['result']['content'][0]['text']
            print(content)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()