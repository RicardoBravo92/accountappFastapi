"""Webhook models for event notifications."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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


class WebhookEndpoint(Base):
    """Webhook endpoint configuration."""
    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    # Endpoint configuration
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)

    # Event subscriptions (JSON array of event types)
    events: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Statistics
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_webhook_endpoint_company", "company_id"),
        Index("idx_webhook_endpoint_active", "is_active"),
    )


class WebhookDelivery(Base):
    """Webhook delivery attempt log."""
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(Integer, ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)

    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)

    # Delivery details
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_webhook_delivery_endpoint", "endpoint_id"),
        Index("idx_webhook_delivery_event", "event_type"),
        Index("idx_webhook_delivery_status", "success"),
        Index("idx_webhook_delivery_created", "started_at"),
    )
