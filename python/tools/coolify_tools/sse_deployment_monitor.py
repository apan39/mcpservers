"""SSE-based real-time deployment monitoring for Coolify."""

import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import requests
from .base import get_coolify_headers, get_coolify_base_url, logger

class DeploymentMonitor:
    """Real-time deployment monitoring with SSE support."""
    
    def __init__(self):
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
    async def start_deployment_with_monitoring(self, app_uuid: str, force: bool = False) -> Dict[str, Any]:
        """Start deployment and begin SSE monitoring."""
        try:
            # Trigger deployment
            base_url = get_coolify_base_url()
            headers = get_coolify_headers()
            
            payload = {"uuid": app_uuid}
            if force:
                payload["force"] = True
            
            response = requests.post(f"{base_url}/deploy", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            deployment_data = response.json()
            deployment_uuid = None
            
            # Parse deployment UUID from response structure (same as working deploy_application)
            if 'deployments' in deployment_data and deployment_data['deployments']:
                deployment_info = deployment_data['deployments'][0]
                deployment_uuid = deployment_info.get('deployment_uuid')
            else:
                # Fallback to other possible locations
                deployment_uuid = deployment_data.get('uuid', deployment_data.get('deployment_uuid'))
            
            if not deployment_uuid:
                # Debug: Show the full response structure
                logger.error(f"DEBUG - Full API response: {json.dumps(deployment_data, indent=2)}")
                
                # Try to extract any potential deployment info
                deployment_keys = [k for k in deployment_data.keys() if 'deploy' in k.lower()]
                uuid_keys = [k for k in deployment_data.keys() if 'uuid' in k.lower() or 'id' in k.lower()]
                logger.error(f"DEBUG - Keys with 'deploy': {deployment_keys}")
                logger.error(f"DEBUG - Keys with 'uuid/id': {uuid_keys}")
                
                raise ValueError(f"No deployment UUID returned from API. Response keys: {list(deployment_data.keys())}")
            
            # Initialize monitoring
            monitor_data = {
                'app_uuid': app_uuid,
                'deployment_uuid': deployment_uuid,
                'status': 'started',
                'started_at': datetime.now().isoformat(),
                'last_check': time.time(),
                'progress_events': [],
                'completed': False,
                'success': None
            }
            
            self.active_deployments[deployment_uuid] = monitor_data
            
            # Start background monitoring task
            task = asyncio.create_task(self._monitor_deployment(deployment_uuid))
            self.monitoring_tasks[deployment_uuid] = task
            
            logger.info(f"Started deployment monitoring for {deployment_uuid}")
            
            return {
                'deployment_uuid': deployment_uuid,
                'app_uuid': app_uuid,
                'status': 'monitoring_started',
                'message': 'Deployment triggered and monitoring started'
            }
            
        except Exception as e:
            logger.error(f"Failed to start deployment monitoring: {e}")
            raise
    
    async def _monitor_deployment(self, deployment_uuid: str):
        """Background task to monitor deployment progress."""
        monitor_data = self.active_deployments[deployment_uuid]
        
        try:
            while not monitor_data['completed']:
                # Check deployment status
                status_update = await self._check_deployment_status(deployment_uuid)
                
                if status_update:
                    # Update monitor data
                    monitor_data['status'] = status_update['status']
                    monitor_data['last_check'] = time.time()
                    monitor_data['progress_events'].append({
                        'timestamp': datetime.now().isoformat(),
                        'status': status_update['status'],
                        'details': status_update.get('details', {})
                    })
                    
                    # Check if deployment completed
                    if status_update['status'] in ['success', 'failed', 'cancelled']:
                        monitor_data['completed'] = True
                        monitor_data['success'] = status_update['status'] == 'success'
                        monitor_data['finished_at'] = datetime.now().isoformat()
                        
                        logger.info(f"Deployment {deployment_uuid} completed with status: {status_update['status']}")
                        break
                
                # Wait before next check (avoid overwhelming API)
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Error monitoring deployment {deployment_uuid}: {e}")
            monitor_data['status'] = 'monitoring_error'
            monitor_data['error'] = str(e)
        finally:
            # Cleanup
            if deployment_uuid in self.monitoring_tasks:
                del self.monitoring_tasks[deployment_uuid]
    
    async def _check_deployment_status(self, deployment_uuid: str) -> Optional[Dict[str, Any]]:
        """Check current deployment status via API."""
        try:
            base_url = get_coolify_base_url()
            headers = get_coolify_headers()
            
            response = requests.get(f"{base_url}/deployments/{deployment_uuid}", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'status': data.get('status', 'unknown'),
                'details': {
                    'application_name': data.get('application_name'),
                    'started_at': data.get('started_at'),
                    'finished_at': data.get('finished_at'),
                    'logs_count': len(data.get('logs', []))
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to check deployment status for {deployment_uuid}: {e}")
            return None
    
    async def get_deployment_stream(self, deployment_uuid: str) -> AsyncGenerator[str, None]:
        """Generate SSE stream for deployment updates."""
        if deployment_uuid not in self.active_deployments:
            yield f"data: {json.dumps({'error': 'Deployment not found'})}\n\n"
            return
        
        monitor_data = self.active_deployments[deployment_uuid]
        sent_events = 0
        
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'deployment_uuid': deployment_uuid, 'status': monitor_data['status'], 'started_at': monitor_data['started_at']})}\n\n"
            
            while not monitor_data['completed']:
                # Send new progress events
                events = monitor_data['progress_events'][sent_events:]
                for event in events:
                    yield f"data: {json.dumps({'type': 'progress', 'deployment_uuid': deployment_uuid, **event})}\n\n"
                    sent_events += 1
                
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                
                await asyncio.sleep(2)
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'completed', 'deployment_uuid': deployment_uuid, 'success': monitor_data['success'], 'finished_at': monitor_data.get('finished_at')})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in deployment stream for {deployment_uuid}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            # Cleanup after stream ends
            if deployment_uuid in self.active_deployments:
                # Keep for a short time for potential reconnections
                asyncio.create_task(self._cleanup_deployment_data(deployment_uuid, delay=300))
    
    async def _cleanup_deployment_data(self, deployment_uuid: str, delay: int = 300):
        """Clean up deployment data after delay."""
        await asyncio.sleep(delay)
        if deployment_uuid in self.active_deployments:
            del self.active_deployments[deployment_uuid]
            logger.info(f"Cleaned up deployment data for {deployment_uuid}")
    
    def get_deployment_status(self, deployment_uuid: str) -> Optional[Dict[str, Any]]:
        """Get current deployment status synchronously."""
        return self.active_deployments.get(deployment_uuid)
    
    def list_active_deployments(self) -> Dict[str, Dict[str, Any]]:
        """List all currently monitored deployments."""
        return self.active_deployments.copy()
    
    def stop_monitoring(self, deployment_uuid: str) -> bool:
        """Stop monitoring a specific deployment."""
        if deployment_uuid in self.monitoring_tasks:
            task = self.monitoring_tasks[deployment_uuid]
            task.cancel()
            del self.monitoring_tasks[deployment_uuid]
            
        if deployment_uuid in self.active_deployments:
            del self.active_deployments[deployment_uuid]
            
        logger.info(f"Stopped monitoring deployment {deployment_uuid}")
        return True

# Global deployment monitor instance
deployment_monitor = DeploymentMonitor()