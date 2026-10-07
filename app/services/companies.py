from typing import Optional, List
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def get_company(db: Session, company_id: int, current_user) -> Company:
    """Get a company by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise NotFoundError("Company", company_id)
    return company


def update_company(db: Session, company_id: int, company_data: CompanyUpdate, current_user) -> Company:
    """Update a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise NotFoundError("Company", company_id)
    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: int, current_user) -> Company:
    """Soft delete a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise NotFoundError("Company", company_id)
    company.is_active = False
    db.commit()
    return company


def create_company(db: Session, company_data: CompanyCreate, current_user) -> Company:
    """Create a new company."""
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def list_companies(db: Session, current_user) -> List[Company]:
    """List all active companies."""
    return db.query(Company).filter(Company.is_active == True).all()