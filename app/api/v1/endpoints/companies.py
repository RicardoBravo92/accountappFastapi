from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    COMPANY_PERMISSIONS,
    require_permission,
    require_role,
    UserRole,
)
from app.models.auth.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.companies import (
    list_companies,
    create_company,
    get_company,
    update_company,
    delete_company,
)

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get(
    "/",
    response_model=list[CompanyResponse],
    summary="List all companies",
    description="Retrieve a list of all active companies accessible to the current user.",
    response_description="List of companies",
)
def list_companies_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(COMPANY_PERMISSIONS["list"])),
):
    return list_companies(db, current_user)

@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
    description="Create a new company with name, contact information, and settings. Requires company:create permission.",
    response_description="Created company",
)
def create_company_endpoint(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(COMPANY_PERMISSIONS["create"])),
):
    return create_company(db, company_data, current_user)

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get company by ID",
    description="Retrieve detailed information about a specific company. Requires company:read permission.",
    response_description="Company details",
)
def get_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(COMPANY_PERMISSIONS["read"])),
):
    return get_company(db, company_id, current_user)

@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update company",
    description="Update an existing company's information. Requires company:update permission.",
    response_description="Updated company",
)
def update_company_endpoint(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(COMPANY_PERMISSIONS["update"])),
):
    return update_company(db, company_id, company_data, current_user)

@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company",
    description="Soft delete a company (marks as inactive). Requires company:delete permission.",
    response_description="Company deleted successfully",
)
def delete_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(COMPANY_PERMISSIONS["delete"])),
):
    delete_company(db, company_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
