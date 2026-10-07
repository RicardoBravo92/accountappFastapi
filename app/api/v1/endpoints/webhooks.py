from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    WEBHOOK_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.webhook import (
    WebhookEndpointCreate,
    WebhookEndpointUpdate,
    WebhookEndpointResponse,
    WebhookDeliveryResponse,
    WebhookEndpointStats,
    WebhookEvent,
)
from app.services.webhooks import WebhookManager, trigger_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/", response_model=list[WebhookEndpointResponse])
def list_webhooks(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["list"])),
):
    """List all webhook endpoints for the current user's company."""
    manager = WebhookManager(db)
    endpoints = manager.list_endpoints(current_user.companies[0].id if current_user.companies else 0, active_only)
    return endpoints


@router.post("/", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_data: WebhookEndpointCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["create"])),
):
    """Create a new webhook endpoint."""
    # Get user's company (first one if multiple)
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    endpoint = manager.create_endpoint(
        company_id=company_id,
        url=str(webhook_data.url),
        events=webhook_data.events,
        secret=webhook_data.secret,
        max_retries=webhook_data.max_retries,
        retry_delay_seconds=webhook_data.retry_delay_seconds,
    )
    
    # Audit log
    from app.services.audit import AuditLogger, AuditAction
    audit = AuditLogger(db)
    audit.log(
        action=WebhookAction.WEBHOOK_CREATE,
        user_id=current_user.id,
        company_id=company_id,
        resource_type="webhook",
        resource_id=endpoint.id,
        request=request,
        status_code=201,
        details={"url": str(webhook_data.url), "events": webhook_data.events},
    )
    
    return endpoint


@router.get("/{webhook_id}", response_model=WebhookEndpointResponse)
def get_webhook(
    webhook_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["read"])),
):
    """Get a webhook endpoint by ID."""
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    endpoint = manager.get_endpoint(webhook_id, company_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    return endpoint


@router.put("/{webhook_id}", response_model=WebhookEndpointResponse)
def update_webhook(
    webhook_id: int,
    webhook_data: WebhookEndpointUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["update"])),
):
    """Update a webhook endpoint."""
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    endpoint = manager.update_endpoint(
        endpoint_id=webhook_id,
        company_id=company_id,
        url=str(webhook_data.url) if webhook_data.url else None,
        events=webhook_data.events,
        secret=webhook_data.secret,
        is_active=webhook_data.is_active,
        max_retries=webhook_data.max_retries,
        retry_delay_seconds=webhook_data.retry_delay_seconds,
    )
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    # Audit log
    from app.services.audit import AuditLogger, AuditAction
    audit = AuditLogger(db)
    audit.log(
        action=AuditAction.WEBHOOK_UPDATE,
        user_id=current_user.id,
        company_id=company_id,
        resource_type="webhook",
        resource_id=webhook_id,
        request=request,
        status_code=200,
        details=webhook_data.model_dump(exclude_unset=True),
    )
    
    return endpoint


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["delete"])),
):
    """Delete a webhook endpoint."""
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    success = manager.delete_endpoint(webhook_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    # Audit log
    from app.services.audit import AuditLogger, AuditAction
    audit = AuditLogger(db)
    audit.log(
        action=AuditAction.WEBHOOK_DELETE,
        user_id=current_user.id,
        company_id=company_id,
        resource_type="webhook",
        resource_id=webhook_id,
        request=request,
        status_code=204,
    )
    
    return None


@router.get("/{webhook_id}/deliveries", response_model=list[WebhookDeliveryResponse])
def list_webhook_deliveries(
    webhook_id: int,
    success: bool | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["read"])),
):
    """List delivery logs for a webhook endpoint."""
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    endpoint = manager.get_endpoint(webhook_id, company_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    deliveries = manager.get_delivery_logs(
        endpoint_id=webhook_id,
        success=success,
        limit=limit,
        offset=offset,
    )
    return deliveries


@router.get("/{webhook_id}/stats", response_model=WebhookEndpointStats)
def get_webhook_stats(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(WEBHOOK_PERMISSIONS["read"])),
):
    """Get statistics for a webhook endpoint."""
    company_id = current_user.companies[0].id if current_user.companies else 0
    if not company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
    
    manager = WebhookManager(db)
    endpoint = manager.get_endpoint(webhook_id, company_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    return stats