"""Webhook schemas."""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from app.schemas.sanitized_base import SanitizedBaseModel, SanitizedStr


class WebhookEvent(str, Enum):
    """Types of webhook events."""
    # Invoice events
    INVOICE_CREATED = "invoice.created"
    INVOICE_UPDATED = "invoice.updated"
    INVOICE_DELETED = "invoice.deleted"
    INVOICE_SENT = "invoice.sent"
    INVOICE_PAID = "invoice.paid"
    INVOICE_OVERDUE = "invoice.overdue"
    
    # Bill events
    BILL_CREATED = "bill.created"
    BILL_UPDATED = "bill.updated"
    BILL_DELETED = "bill.deleted"
    BILL_PAID = "bill.paid"
    BILL_OVERDUE = "bill.overdue"
    
    # Contact events
    CONTACT_CREATED = "contact.created"
    CONTACT_UPDATED = "contact.updated"
    CONTACT_DELETED = "contact.deleted"
    
    # Account events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_UPDATED = "account.updated"
    ACCOUNT_DELETED = "account.deleted"
    
    # Transaction events
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_UPDATED = "transaction.updated"
    TRANSACTION_DELETED = "transaction.deleted"
    
    # Payment events
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_SENT = "payment.sent"
    PAYMENT_FAILED = "payment.failed"
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Company events
    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"
    COMPANY_DELETED = "company.deleted"
    
    # Webhook events
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_UPDATED = "webhook.updated"
    WEBHOOK_DELETED = "webhook.deleted"
    WEBHOOK_TRIGGERED = "webhook.triggered"


class WebhookEndpointBase(SanitizedBaseModel):
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    events: list[str] = Field(..., description="List of event types to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for signature verification (auto-generated if not provided)")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum number of retry attempts")
    retry_delay_seconds: int = Field(60, ge=1, le=3600, description="Delay between retries in seconds")


class WebhookEndpointCreate(WebhookEndpointBase):
    pass


class WebhookEndpointUpdate(SanitizedBaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[list[str]] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=1, le=3600)


class WebhookEndpointResponse(WebhookEndpointBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    last_error: Optional[str] = None

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: int
    endpoint_id: int
    event_type: str
    attempt: int
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    success: bool

    class Config:
        from_attributes = True


class WebhookEndpointStats(BaseModel):
    endpoint_id: int
    url: str
    is_active: bool
    events: list[str]
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    last_triggered_at: Optional[datetime] = None
    last_error: Optional[str] = None


class WebhookPayload(BaseModel):
    event: str
    timestamp: str
    company_id: int
    data: dict
    webhook_id: int
    delivery_id: Optional[int] = None
    signature: Optional[str] = None