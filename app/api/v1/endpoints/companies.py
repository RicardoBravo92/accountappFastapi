from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
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

@router.get("/", response_model=list[CompanyResponse])
def list_companies_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_companies(db, current_user)

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company_endpoint(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_company(db, company_data, current_user)

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_company(db, company_id, current_user)

@router.put("/{company_id}", response_model=CompanyResponse)
def update_company_endpoint(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_company(db, company_id, company_data, current_user)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_company(db, company_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
