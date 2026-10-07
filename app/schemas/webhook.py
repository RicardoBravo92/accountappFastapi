"""Webhook schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.sanitized_base import SanitizedBaseModel


class WebhookEvent(StrEnum):
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
    secret: str | None = Field(None, description="Secret for signature verification (auto-generated if not provided)")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum number of retry attempts")
    retry_delay_seconds: int = Field(60, ge=1, le=3600, description="Delay between retries in seconds")


class WebhookEndpointCreate(WebhookEndpointBase):
    pass


class WebhookEndpointUpdate(SanitizedBaseModel):
    url: HttpUrl | None = None
    events: list[str] | None = None
    secret: str | None = None
    is_active: bool | None = None
    max_retries: int | None = Field(None, ge=0, le=10)
    retry_delay_seconds: int | None = Field(None, ge=1, le=3600)


class WebhookEndpointResponse(WebhookEndpointBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None
    success_count: int = 0
    failure_count: int = 0
    last_error: str | None = None

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: int
    endpoint_id: int
    event_type: str
    attempt: int
    status_code: int | None = None
    response_body: str | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
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
    last_triggered_at: datetime | None = None
    last_error: str | None = None


class WebhookPayload(BaseModel):
    event: str
    timestamp: str
    company_id: int
    data: dict
    webhook_id: int
    delivery_id: int | None = None
    signature: str | None = None
