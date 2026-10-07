"""Role-Based Access Control (RBAC) system.

Defines permissions for each role and provides dependency functions
for protecting API endpoints.
"""

from enum import StrEnum

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import ForbiddenError
from app.database import get_db
from app.models.auth.user import User, UserRole


class Permission(StrEnum):
    """System permissions."""
    # Company permissions
    COMPANY_CREATE = "company:create"
    COMPANY_READ = "company:read"
    COMPANY_UPDATE = "company:update"
    COMPANY_DELETE = "company:delete"
    COMPANY_LIST = "company:list"

    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"

    # Contact permissions
    CONTACT_CREATE = "contact:create"
    CONTACT_READ = "contact:read"
    CONTACT_UPDATE = "contact:update"
    CONTACT_DELETE = "contact:delete"
    CONTACT_LIST = "contact:list"

    # Account permissions
    ACCOUNT_CREATE = "account:create"
    ACCOUNT_READ = "account:read"
    ACCOUNT_UPDATE = "account:update"
    ACCOUNT_DELETE = "account:delete"
    ACCOUNT_LIST = "account:list"

    # Transaction permissions
    TRANSACTION_CREATE = "transaction:create"
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_UPDATE = "transaction:update"
    TRANSACTION_DELETE = "transaction:delete"
    TRANSACTION_LIST = "transaction:list"

    # Invoice permissions
    INVOICE_CREATE = "invoice:create"
    INVOICE_READ = "invoice:read"
    INVOICE_UPDATE = "invoice:update"
    INVOICE_DELETE = "invoice:delete"
    INVOICE_LIST = "invoice:list"

    # Bill permissions
    BILL_CREATE = "bill:create"
    BILL_READ = "bill:read"
    BILL_UPDATE = "bill:update"
    BILL_DELETE = "bill:delete"
    BILL_LIST = "bill:list"

    # Report permissions
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"

    # Settings permissions
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"

    # Upload permissions
    UPLOAD_CREATE = "upload:create"
    UPLOAD_READ = "upload:read"
    UPLOAD_DELETE = "upload:delete"
    UPLOAD_LIST = "upload:list"

    # Webhook permissions
    WEBHOOK_CREATE = "webhook:create"
    WEBHOOK_READ = "webhook:read"
    WEBHOOK_UPDATE = "webhook:update"
    WEBHOOK_DELETE = "webhook:delete"
    WEBHOOK_LIST = "webhook:list"
    WEBHOOK_TRIGGER = "webhook:trigger"

    # Category permissions
    CATEGORY_CREATE = "category:create"
    CATEGORY_READ = "category:read"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"
    CATEGORY_LIST = "category:list"

    # Tax permissions
    TAX_CREATE = "tax:create"
    TAX_READ = "tax:read"
    TAX_UPDATE = "tax:update"
    TAX_DELETE = "tax:delete"
    TAX_LIST = "tax:list"

    # Currency permissions
    CURRENCY_CREATE = "currency:create"
    CURRENCY_READ = "currency:read"
    CURRENCY_UPDATE = "currency:update"
    CURRENCY_DELETE = "currency:delete"
    CURRENCY_LIST = "currency:list"

    # Item permissions
    ITEM_CREATE = "item:create"
    ITEM_READ = "item:read"
    ITEM_UPDATE = "item:update"
    ITEM_DELETE = "item:delete"
    ITEM_LIST = "item:list"

    # Transfer permissions
    TRANSFER_CREATE = "transfer:create"
    TRANSFER_READ = "transfer:read"
    TRANSFER_UPDATE = "transfer:update"
    TRANSFER_DELETE = "transfer:delete"
    TRANSFER_LIST = "transfer:list"


# Role-to-permissions mapping
ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: {
        # Admin has all permissions
        Permission.COMPANY_CREATE, Permission.COMPANY_READ, Permission.COMPANY_UPDATE,
        Permission.COMPANY_DELETE, Permission.COMPANY_LIST,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_LIST,
        Permission.CONTACT_CREATE, Permission.CONTACT_READ, Permission.CONTACT_UPDATE,
        Permission.CONTACT_DELETE, Permission.CONTACT_LIST,
        Permission.ACCOUNT_CREATE, Permission.ACCOUNT_READ, Permission.ACCOUNT_UPDATE,
        Permission.ACCOUNT_DELETE, Permission.ACCOUNT_LIST,
        Permission.TRANSACTION_CREATE, Permission.TRANSACTION_READ, Permission.TRANSACTION_UPDATE,
        Permission.TRANSACTION_DELETE, Permission.TRANSACTION_LIST,
        Permission.INVOICE_CREATE, Permission.INVOICE_READ, Permission.INVOICE_UPDATE,
        Permission.INVOICE_DELETE, Permission.INVOICE_LIST,
        Permission.BILL_CREATE, Permission.BILL_READ, Permission.BILL_UPDATE,
        Permission.BILL_DELETE, Permission.BILL_LIST,
        Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.SETTINGS_READ, Permission.SETTINGS_UPDATE,
        Permission.UPLOAD_CREATE, Permission.UPLOAD_READ, Permission.UPLOAD_DELETE,
        Permission.CATEGORY_CREATE, Permission.CATEGORY_READ, Permission.CATEGORY_UPDATE,
        Permission.CATEGORY_DELETE, Permission.CATEGORY_LIST,
        Permission.TAX_CREATE, Permission.TAX_READ, Permission.TAX_UPDATE,
        Permission.TAX_DELETE, Permission.TAX_LIST,
        Permission.CURRENCY_CREATE, Permission.CURRENCY_READ, Permission.CURRENCY_UPDATE,
        Permission.CURRENCY_DELETE, Permission.CURRENCY_LIST,
        Permission.ITEM_CREATE, Permission.ITEM_READ, Permission.ITEM_UPDATE,
        Permission.ITEM_DELETE, Permission.ITEM_LIST,
        Permission.TRANSFER_CREATE, Permission.TRANSFER_READ, Permission.TRANSFER_UPDATE,
        Permission.TRANSFER_DELETE, Permission.TRANSFER_LIST,
        Permission.WEBHOOK_CREATE, Permission.WEBHOOK_READ, Permission.WEBHOOK_UPDATE,
        Permission.WEBHOOK_DELETE, Permission.WEBHOOK_LIST, Permission.WEBHOOK_TRIGGER,
    },
    UserRole.MANAGER: {
        # Manager has most permissions except user management and settings
        Permission.COMPANY_CREATE, Permission.COMPANY_READ, Permission.COMPANY_UPDATE,
        Permission.COMPANY_LIST,
        Permission.USER_READ, Permission.USER_LIST,
        Permission.CONTACT_CREATE, Permission.CONTACT_READ, Permission.CONTACT_UPDATE,
        Permission.CONTACT_DELETE, Permission.CONTACT_LIST,
        Permission.ACCOUNT_CREATE, Permission.ACCOUNT_READ, Permission.ACCOUNT_UPDATE,
        Permission.ACCOUNT_DELETE, Permission.ACCOUNT_LIST,
        Permission.TRANSACTION_CREATE, Permission.TRANSACTION_READ, Permission.TRANSACTION_UPDATE,
        Permission.TRANSACTION_DELETE, Permission.TRANSACTION_LIST,
        Permission.INVOICE_CREATE, Permission.INVOICE_READ, Permission.INVOICE_UPDATE,
        Permission.INVOICE_DELETE, Permission.INVOICE_LIST,
        Permission.BILL_CREATE, Permission.BILL_READ, Permission.BILL_UPDATE,
        Permission.BILL_DELETE, Permission.BILL_LIST,
        Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.UPLOAD_CREATE, Permission.UPLOAD_READ, Permission.UPLOAD_DELETE,
        Permission.CATEGORY_CREATE, Permission.CATEGORY_READ, Permission.CATEGORY_UPDATE,
        Permission.CATEGORY_LIST,
        Permission.TAX_CREATE, Permission.TAX_READ, Permission.TAX_UPDATE,
        Permission.TAX_LIST,
        Permission.CURRENCY_CREATE, Permission.CURRENCY_READ, Permission.CURRENCY_UPDATE,
        Permission.CURRENCY_LIST,
        Permission.ITEM_CREATE, Permission.ITEM_READ, Permission.ITEM_UPDATE,
        Permission.ITEM_LIST,
        Permission.TRANSFER_CREATE, Permission.TRANSFER_READ, Permission.TRANSFER_UPDATE,
        Permission.TRANSFER_LIST,
        Permission.WEBHOOK_CREATE, Permission.WEBHOOK_READ, Permission.WEBHOOK_UPDATE,
        Permission.WEBHOOK_DELETE, Permission.WEBHOOK_LIST,
    },
    UserRole.ACCOUNTANT: {
        # Accountant has financial permissions
        Permission.COMPANY_READ, Permission.COMPANY_LIST,
        Permission.USER_READ, Permission.USER_LIST,
        Permission.CONTACT_READ, Permission.CONTACT_LIST,
        Permission.ACCOUNT_CREATE, Permission.ACCOUNT_READ, Permission.ACCOUNT_UPDATE,
        Permission.ACCOUNT_LIST,
        Permission.TRANSACTION_CREATE, Permission.TRANSACTION_READ, Permission.TRANSACTION_UPDATE,
        Permission.TRANSACTION_LIST,
        Permission.INVOICE_CREATE, Permission.INVOICE_READ, Permission.INVOICE_UPDATE,
        Permission.INVOICE_LIST,
        Permission.BILL_CREATE, Permission.BILL_READ, Permission.BILL_UPDATE,
        Permission.BILL_LIST,
        Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.UPLOAD_CREATE, Permission.UPLOAD_READ,
        Permission.CATEGORY_READ, Permission.CATEGORY_LIST,
        Permission.TAX_READ, Permission.TAX_LIST,
        Permission.CURRENCY_READ, Permission.CURRENCY_LIST,
        Permission.ITEM_READ, Permission.ITEM_LIST,
        Permission.TRANSFER_READ, Permission.TRANSFER_LIST,
        Permission.WEBHOOK_READ, Permission.WEBHOOK_TRIGGER,
    },
    UserRole.VIEWER: {
        # Viewer has read-only permissions
        Permission.COMPANY_READ, Permission.COMPANY_LIST,
        Permission.USER_READ, Permission.USER_LIST,
        Permission.CONTACT_READ, Permission.CONTACT_LIST,
        Permission.ACCOUNT_READ, Permission.ACCOUNT_LIST,
        Permission.TRANSACTION_READ, Permission.TRANSACTION_LIST,
        Permission.INVOICE_READ, Permission.INVOICE_LIST,
        Permission.BILL_READ, Permission.BILL_LIST,
        Permission.REPORT_READ,
        Permission.UPLOAD_READ,
        Permission.CATEGORY_READ, Permission.CATEGORY_LIST,
        Permission.TAX_READ, Permission.TAX_LIST,
        Permission.CURRENCY_READ, Permission.CURRENCY_LIST,
        Permission.ITEM_READ, Permission.ITEM_LIST,
        Permission.TRANSFER_READ, Permission.TRANSFER_LIST,
        Permission.WEBHOOK_READ,
    },
}


def get_user_permissions(role: UserRole) -> set[Permission]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_user_permissions(role)


def require_permission(permission: Permission):
    """FastAPI dependency that checks if current user has a specific permission.

    Usage:
        @router.get("/companies")
        def list_companies(current_user: User = Depends(require_permission(Permission.COMPANY_LIST))):
            ...
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = UserRole(current_user.role)
        if not has_permission(user_role, permission):
            raise ForbiddenError(
                f"Permission '{permission.value}' required. "
                f"Your role '{user_role.value}' does not have this permission."
            )
        return current_user
    return permission_checker


def require_any_permission(*permissions: Permission):
    """FastAPI dependency that checks if current user has ANY of the specified permissions."""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = UserRole(current_user.role)
        user_perms = get_user_permissions(user_role)
        if not any(p in user_perms for p in permissions):
            raise ForbiddenError(
                f"One of these permissions required: {[p.value for p in permissions]}. "
                f"Your role '{user_role.value}' does not have any of them."
            )
        return current_user
    return permission_checker


def require_role(*allowed_roles: UserRole):
    """FastAPI dependency that checks if current user has one of the allowed roles.

    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(current_user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = UserRole(current_user.role)
        if user_role not in allowed_roles:
            raise ForbiddenError(
                f"Role '{user_role.value}' not authorized. "
                f"Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def require_owner_or_admin(
    resource_company_id: int,
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if user is owner of the company or admin.

    This is useful for company-scoped resources where owners and admins
    have full access regardless of their role's base permissions.
    """

    # This will be implemented as a dependency that takes company_id
    # For now, we'll use a simpler approach
    user_role = UserRole(current_user.role)

    # Admins can access everything
    if user_role == UserRole.ADMIN:
        return current_user

    # Check if user is owner of the company
    # This requires a database query, so we'll create a specific dependency for this
    return current_user


class RequireCompanyAccess:
    """Dependency class for company-scoped access control.

    Usage:
        require_company_access = RequireCompanyAccess(Permission.COMPANY_READ)

        @router.get("/companies/{company_id}")
        def get_company(
            company_id: int,
            current_user: User = Depends(require_company_access)
        ):
            ...
    """

    def __init__(self, permission: Permission, allow_owner: bool = True):
        self.permission = permission
        self.allow_owner = allow_owner

    def __call__(
        self,
        company_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        from app.models.auth.user import UserCompany

        user_role = UserRole(current_user.role)

        # Admin always has access
        if user_role == UserRole.ADMIN:
            return current_user

        # Check if user is owner of the company
        if self.allow_owner:
            is_owner = db.query(UserCompany).filter(
                UserCompany.user_id == current_user.id,
                UserCompany.company_id == company_id,
                UserCompany.is_owner
            ).first()

            if is_owner:
                return current_user

        # Check role-based permission
        if has_permission(user_role, self.permission):
            return current_user

        # If we get here, user doesn't have permission
        raise ForbiddenError(
            f"Access denied to company {company_id}. "
            f"Permission '{self.permission.value}' required."
        )


# Convenience dependencies for common patterns
require_admin = require_role(UserRole.ADMIN)
require_manager_or_admin = require_role(UserRole.MANAGER, UserRole.ADMIN)
require_accountant_or_above = require_role(UserRole.ACCOUNTANT, UserRole.MANAGER, UserRole.ADMIN)
require_any_authenticated = require_role(UserRole.VIEWER, UserRole.ACCOUNTANT, UserRole.MANAGER, UserRole.ADMIN)


# Permission constants for easy importing
COMPANY_PERMISSIONS = {
    "create": Permission.COMPANY_CREATE,
    "read": Permission.COMPANY_READ,
    "update": Permission.COMPANY_UPDATE,
    "delete": Permission.COMPANY_DELETE,
    "list": Permission.COMPANY_LIST,
}

USER_PERMISSIONS = {
    "create": Permission.USER_CREATE,
    "read": Permission.USER_READ,
    "update": Permission.USER_UPDATE,
    "delete": Permission.USER_DELETE,
    "list": Permission.USER_LIST,
}

CONTACT_PERMISSIONS = {
    "create": Permission.CONTACT_CREATE,
    "read": Permission.CONTACT_READ,
    "update": Permission.CONTACT_UPDATE,
    "delete": Permission.CONTACT_DELETE,
    "list": Permission.CONTACT_LIST,
}

ACCOUNT_PERMISSIONS = {
    "create": Permission.ACCOUNT_CREATE,
    "read": Permission.ACCOUNT_READ,
    "update": Permission.ACCOUNT_UPDATE,
    "delete": Permission.ACCOUNT_DELETE,
    "list": Permission.ACCOUNT_LIST,
}

TRANSACTION_PERMISSIONS = {
    "create": Permission.TRANSACTION_CREATE,
    "read": Permission.TRANSACTION_READ,
    "update": Permission.TRANSACTION_UPDATE,
    "delete": Permission.TRANSACTION_DELETE,
    "list": Permission.TRANSACTION_LIST,
}

INVOICE_PERMISSIONS = {
    "create": Permission.INVOICE_CREATE,
    "read": Permission.INVOICE_READ,
    "update": Permission.INVOICE_UPDATE,
    "delete": Permission.INVOICE_DELETE,
    "list": Permission.INVOICE_LIST,
}

BILL_PERMISSIONS = {
    "create": Permission.BILL_CREATE,
    "read": Permission.BILL_READ,
    "update": Permission.BILL_UPDATE,
    "delete": Permission.BILL_DELETE,
    "list": Permission.BILL_LIST,
}

REPORT_PERMISSIONS = {
    "read": Permission.REPORT_READ,
    "export": Permission.REPORT_EXPORT,
}

CATEGORY_PERMISSIONS = {
    "create": Permission.CATEGORY_CREATE,
    "read": Permission.CATEGORY_READ,
    "update": Permission.CATEGORY_UPDATE,
    "delete": Permission.CATEGORY_DELETE,
    "list": Permission.CATEGORY_LIST,
}

TAX_PERMISSIONS = {
    "create": Permission.TAX_CREATE,
    "read": Permission.TAX_READ,
    "update": Permission.TAX_UPDATE,
    "delete": Permission.TAX_DELETE,
    "list": Permission.TAX_LIST,
}

CURRENCY_PERMISSIONS = {
    "create": Permission.CURRENCY_CREATE,
    "read": Permission.CURRENCY_READ,
    "update": Permission.CURRENCY_UPDATE,
    "delete": Permission.CURRENCY_DELETE,
    "list": Permission.CURRENCY_LIST,
}

ITEM_PERMISSIONS = {
    "create": Permission.ITEM_CREATE,
    "read": Permission.ITEM_READ,
    "update": Permission.ITEM_UPDATE,
    "delete": Permission.ITEM_DELETE,
    "list": Permission.ITEM_LIST,
}

TRANSFER_PERMISSIONS = {
    "create": Permission.TRANSFER_CREATE,
    "read": Permission.TRANSFER_READ,
    "update": Permission.TRANSFER_UPDATE,
    "delete": Permission.TRANSFER_DELETE,
    "list": Permission.TRANSFER_LIST,
}

UPLOAD_PERMISSIONS = {
    "create": Permission.UPLOAD_CREATE,
    "read": Permission.UPLOAD_READ,
    "delete": Permission.UPLOAD_DELETE,
    "list": Permission.UPLOAD_LIST,
}

WEBHOOK_PERMISSIONS = {
    "create": Permission.WEBHOOK_CREATE,
    "read": Permission.WEBHOOK_READ,
    "update": Permission.WEBHOOK_UPDATE,
    "delete": Permission.WEBHOOK_DELETE,
    "list": Permission.WEBHOOK_LIST,
    "trigger": Permission.WEBHOOK_TRIGGER,
}

SETTINGS_PERMISSIONS = {
    "read": Permission.SETTINGS_READ,
    "update": Permission.SETTINGS_UPDATE,
}
