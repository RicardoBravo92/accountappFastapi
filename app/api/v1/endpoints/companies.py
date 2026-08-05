from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.companies import company_service

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await company_service["list_companies"](db, current_user)

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await company_service["create_company"](db, company_data, current_user)

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await company_service["get_company"](db, company_id, current_user)

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await company_service["update_company"](db, company_id, company_data, current_user)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await company_service["delete_company"](db, company_id, current_user)
