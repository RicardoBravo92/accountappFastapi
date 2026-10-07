"""Audit logging for sensitive actions."""

import json
from functools import wraps

from app.models.auth.user import AuditAction, AuditLog


def get_client_ip(request) -> str | None:
    """Extract client IP from request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def log_audit(
    db,
    action: AuditAction,
    user_id: int | None = None,
    company_id: int | None = None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    request=None,
    status_code: int | None = None,
    details: dict | None = None,
) -> AuditLog:
    """Create an audit log entry."""

    # Prepare details
    details_json = None
    if details:
        # Remove sensitive fields
        safe_details = {k: v for k, v in details.items()
                       if k.lower() not in ("password", "token", "secret", "key", "refresh_token")}
        if safe_details:
            details_json = json.dumps(safe_details)

    # Extract request info
    ip_address = None
    user_agent = None
    request_method = None
    request_path = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        request_method = request.method
        request_path = str(request.url.path)

    audit_log = AuditLog(
        user_id=user_id,
        company_id=company_id,
        action=action.value,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        request_path=request_path,
        status_code=status_code,
        details=details_json,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def audit_action(
    action: AuditAction,
    resource_type: str | None = None,
    resource_id_param: str | None = None,
    company_id_param: str | None = None,
):
    """Decorator to automatically audit an endpoint action.

    Usage:
        @audit_action(AuditAction.INVOICE_CREATE, "invoice", "invoice_id")
        def create_invoice(invoice_id: int, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get db from kwargs (injected by FastAPI)
            db = kwargs.get("db")
            current_user = kwargs.get("current_user")
            request = kwargs.get("request")

            # Extract resource ID from kwargs or result
            resource_id = kwargs.get(resource_id_param) if resource_id_param else None
            company_id = kwargs.get(company_id_param) if company_id_param else None

            # Execute the function
            try:
                result = await func(*args, **kwargs)

                # Extract resource ID from result if not in kwargs
                if not resource_id and result:
                    if hasattr(result, "id"):
                        resource_id = result.id

                # Extract company ID from result if not in kwargs
                if not company_id and result and hasattr(result, "company_id"):
                    company_id = result.company_id

                # Log success
                if db:
                    log_audit(
                        db=db,
                        action=action,
                        user_id=current_user.id if current_user else None,
                        company_id=company_id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        request=request,
                        status_code=200,
                        details={"result": "success"},
                    )

                return result

            except Exception as e:
                # Log failure
                if db:
                    log_audit(
                        db=db,
                        action=action,
                        user_id=current_user.id if current_user else None,
                        company_id=company_id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        request=request,
                        status_code=getattr(e, "status_code", 500),
                        details={"error": str(e)},
                    )
                raise

        return wrapper
    return decorator


class AuditLogger:
    """High-level audit logger for use in services."""

    def __init__(self, db):
        self.db = db

    def log(
        self,
        action: AuditAction,
        user_id: int | None = None,
        company_id: int | None = None,
        resource_type: str | None = None,
        resource_id: int | None = None,
        request=None,
        status_code: int | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        return log_audit(
            db=self.db,
            action=action,
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            request=request,
            status_code=status_code,
            details=details,
        )

    def login_success(self, user_id: int, request=None):
        return self.log(AuditAction.LOGIN_SUCCESS, user_id=user_id, request=request, status_code=200)

    def login_failed(self, email: str, request=None, reason: str = "invalid_credentials"):
        import hashlib
        # Hash email to avoid PII leakage in audit logs
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:12]
        return self.log(
            AuditAction.LOGIN_FAILED,
            request=request,
            status_code=401,
            details={"email_hash": email_hash, "reason": reason}
        )

    def logout(self, user_id: int, request=None):
        return self.log(AuditAction.LOGOUT, user_id=user_id, request=request, status_code=200)

    def logout_all(self, user_id: int, request=None):
        return self.log(AuditAction.LOGOUT_ALL, user_id=user_id, request=request, status_code=200)

    def token_refresh(self, user_id: int, request=None):
        return self.log(AuditAction.TOKEN_REFRESH, user_id=user_id, request=request, status_code=200)

    def password_change(self, user_id: int, request=None):
        return self.log(AuditAction.PASSWORD_CHANGE, user_id=user_id, request=request, status_code=200)

    def user_create(self, user_id: int, actor_id: int | None = None, request=None):
        return self.log(
            AuditAction.USER_CREATE,
            user_id=actor_id,
            resource_type="user",
            resource_id=user_id,
            request=request,
            status_code=201,
            details={"created_user_id": user_id}
        )

    def user_update(self, user_id: int, actor_id: int | None = None, changes: dict | None = None, request=None):
        return self.log(
            AuditAction.USER_UPDATE,
            user_id=actor_id,
            resource_type="user",
            resource_id=user_id,
            request=request,
            status_code=200,
            details={"changes": changes} if changes else None
        )

    def invoice_create(self, invoice_id: int, user_id: int, company_id: int, request=None):
        return self.log(
            AuditAction.INVOICE_CREATE,
            user_id=user_id,
            company_id=company_id,
            resource_type="invoice",
            resource_id=invoice_id,
            request=request,
            status_code=201,
        )

    def payment_received(self, payment_id: int, user_id: int, company_id: int, amount: float, request=None):
        return self.log(
            AuditAction.PAYMENT_RECEIVED,
            user_id=user_id,
            company_id=company_id,
            resource_type="payment",
            resource_id=payment_id,
            request=request,
            status_code=200,
            details={"amount": amount}
        )
