"""Webhook system for event notifications."""

import json
import hmac
import hashlib
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass
from functools import wraps

import httpx

from app.core.config import settings
from app.models.webhook import WebhookEndpoint, WebhookDelivery, WebhookEvent


@dataclass
class WebhookPayload:
    """Standard webhook payload structure."""
    event: str
    timestamp: str
    company_id: int
    data: dict
    webhook_id: int
    delivery_id: int | None = None


class WebhookManager:
    """Manages webhook endpoints and deliveries."""
    
    def __init__(self, db):
        self.db = db
    
    def create_endpoint(
        self,
        company_id: int,
        url: str,
        events: list[str],
        secret: str | None = None,
        max_retries: int = 3,
        retry_delay_seconds: int = 60,
    ) -> WebhookEndpoint:
        """Create a new webhook endpoint."""
        if secret is None:
            import secrets
            secret = secrets.token_urlsafe(32)
        
        endpoint = WebhookEndpoint(
            company_id=company_id,
            url=url,
            secret=secret,
            events=json.dumps(events),
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        return endpoint
    
    def get_endpoint(self, endpoint_id: int, company_id: int) -> WebhookEndpoint | None:
        """Get a webhook endpoint by ID."""
        return self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == endpoint_id,
            WebhookEndpoint.company_id == company_id
        ).first()
    
    def list_endpoints(self, company_id: int, active_only: bool = True) -> list[WebhookEndpoint]:
        """List webhook endpoints for a company."""
        query = self.db.query(WebhookEndpoint).filter(WebhookEndpoint.company_id == company_id)
        if active_only:
            query = query.filter(WebhookEndpoint.is_active == True)
        return query.all()
    
    def update_endpoint(
        self,
        endpoint_id: int,
        company_id: int,
        url: str | None = None,
        events: list[str] | None = None,
        secret: str | None = None,
        is_active: bool | None = None,
        max_retries: int | None = None,
        retry_delay_seconds: int | None = None,
    ) -> WebhookEndpoint | None:
        """Update a webhook endpoint."""
        endpoint = self.get_endpoint(endpoint_id, company_id)
        if not endpoint:
            return None
        
        if url is not None:
            endpoint.url = url
        if events is not None:
            endpoint.events = json.dumps(events)
        if secret is not None:
            endpoint.secret = secret
        if is_active is not None:
            endpoint.is_active = is_active
        if max_retries is not None:
            endpoint.max_retries = max_retries
        if retry_delay_seconds is not None:
            endpoint.retry_delay_seconds = retry_delay_seconds
        
        endpoint.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(endpoint)
        return endpoint
    
    def delete_endpoint(self, endpoint_id: int, company_id: int) -> bool:
        """Delete a webhook endpoint."""
        endpoint = self.get_endpoint(endpoint_id, company_id)
        if not endpoint:
            return False
        self.db.delete(endpoint)
        self.db.commit()
        return True
    
    def _sign_payload(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    def _create_payload(self, event: WebhookEvent, company_id: int, data: dict, webhook_id: int, delivery_id: int) -> tuple[str, str]:
        """Create webhook payload and signature."""
        payload = WebhookPayload(
            event=event.value,
            timestamp=datetime.now(UTC).isoformat(),
            company_id=company_id,
            data=data,
            webhook_id=webhook_id,
            delivery_id=None,
        )
        payload_json = json.dumps(payload.__dict__, default=str)
        return payload_json, payload_json
    
    async def trigger_event(
        self,
        event: WebhookEvent,
        company_id: int,
        data: dict,
        request=None,
    ) -> list[int]:
        """Trigger a webhook event for all matching endpoints."""
        import httpx
        
        # Get active endpoints subscribed to this event
        endpoints = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.company_id == company_id,
            WebhookEndpoint.is_active == True,
        ).all()
        
        # Filter endpoints subscribed to this event
        matching_endpoints = []
        for endpoint in endpoints:
            subscribed_events = json.loads(endpoint.events)
            if event.value in subscribed_events or "*" in subscribed_events:
                matching_endpoints.append(endpoint)
        
        if not matching_endpoints:
            return []
        
        delivery_ids = []
        
        for endpoint in matching_endpoints:
            # Create delivery record
            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                event_type=event.value,
                payload=json.dumps(data, default=str),
                attempt=1,
            )
            self.db.add(delivery)
            self.db.commit()
            self.db.refresh(delivery)
            
            delivery_ids.append(delivery.id)
            
            # Prepare payload
            payload_data = {
                "event": event.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "company_id": company_id,
                "data": data,
                "webhook_id": endpoint.id,
                "delivery_id": delivery.id,
            }
            payload_json = json.dumps(payload_data, default=str)
            
            # Generate signature
            signature = self._sign_payload(payload_json, endpoint.secret)
            
            # Update payload with signature
            payload_with_sig = {
                **payload_data,
                "signature": signature,
            }
            payload_json = json.dumps(payload_with_sig, default=str)
            
            # Update delivery with payload
            delivery.payload = payload_json
            self.db.commit()
            
            # Trigger async delivery (in background)
            # In production, use a task queue like Celery
            await self._deliver_webhook(endpoint, delivery, payload_json)
        
        return delivery_ids
    
    async def _deliver_webhook(self, endpoint: WebhookEndpoint, delivery: WebhookDelivery, payload: str):
        """Deliver webhook with retry logic."""
        import httpx
        
        max_retries = endpoint.max_retries
        retry_delay = endpoint.retry_delay_seconds
        
        for attempt in range(1, max_retries + 1):
            delivery.attempt = attempt
            delivery.started_at = datetime.now(UTC)
            self.db.commit()
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": self._sign_payload(json.dumps(json.loads(payload), default=str), endpoint.secret),
                        "X-Webhook-Event": json.loads(payload)["event"],
                        "X-Webhook-Delivery": str(delivery.id),
                        "X-Webhook-Timestamp": json.loads(payload)["timestamp"],
                    }
                    
                    response = await client.post(endpoint.url, content=payload, headers=headers)
                    
                    delivery.status_code = response.status_code
                    delivery.response_body = response.text[:1000] if response.text else None
                    delivery.completed_at = datetime.now(UTC)
                    delivery.duration_ms = int((delivery.completed_at - delivery.started_at).total_seconds() * 1000)
                    
                    if 200 <= response.status_code < 300:
                        delivery.success = True
                        endpoint.success_count += 1
                        endpoint.last_triggered_at = datetime.now(UTC)
                        self.db.commit()
                        return
                    else:
                        delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                        
            except Exception as e:
                delivery.error_message = str(e)
                delivery.completed_at = datetime.now(UTC)
                if delivery.started_at:
                    delivery.duration_ms = int((delivery.completed_at - delivery.started_at).total_seconds() * 1000)
            
            # If not last attempt, wait before retry
            if attempt < max_retries:
                import asyncio
                await asyncio.sleep(retry_delay)
        
        # All retries failed
        delivery.success = False
        endpoint.failure_count += 1
        endpoint.last_error = delivery.error_message
        self.db.commit()
    
    def get_delivery_logs(
        self,
        endpoint_id: int | None = None,
        company_id: int | None = None,
        event_type: str | None = None,
        success: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WebhookDelivery]:
        """Get webhook delivery logs."""
        query = self.db.query(WebhookDelivery)
        
        if endpoint_id:
            query = query.filter(WebhookDelivery.endpoint_id == endpoint_id)
        if company_id:
            # Join with endpoints to filter by company
            from app.models.webhook import WebhookEndpoint
            query = query.join(WebhookEndpoint).filter(WebhookEndpoint.company_id == company_id)
        if event_type:
            query = query.filter(WebhookDelivery.event_type == event_type)
        if success is not None:
            query = query.filter(WebhookDelivery.success == success)
        
        return query.order_by(WebhookDelivery.started_at.desc()).offset(offset).limit(limit).all()
    
    def get_endpoint_stats(self, endpoint_id: int) -> dict:
        """Get statistics for a webhook endpoint."""
        endpoint = self.db.query(WebhookEndpoint).filter(WebhookEndpoint.id == endpoint_id).first()
        if not endpoint:
            return {}
        
        total_deliveries = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.endpoint_id == endpoint_id
        ).count()
        
        successful_deliveries = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.endpoint_id == endpoint_id,
            WebhookDelivery.success == True
        ).count()
        
        failed_deliveries = total_deliveries - successful_deliveries
        
        return {
            "endpoint_id": endpoint.id,
            "url": endpoint.url,
            "is_active": endpoint.is_active,
            "events": json.loads(endpoint.events),
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "success_rate": successful_deliveries / total_deliveries if total_deliveries > 0 else 0,
            "last_triggered_at": endpoint.last_triggered_at,
            "last_error": endpoint.last_error,
        }


# Convenience function to trigger webhooks from services
async def trigger_webhook(
    db,
    event: WebhookEvent,
    company_id: int,
    data: dict,
    request=None,
) -> list[int]:
    """Trigger a webhook event."""
    manager = WebhookManager(db)
    return await manager.trigger_event(event, company_id, data, request)