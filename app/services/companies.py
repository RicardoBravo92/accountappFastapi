

from app.models import Company
from fastapi import HTTPException

async def get_company( db, company_id, current_user):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

async def update_company( db, company_id, company_data, current_user):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company

async def delete_company( db, company_id, current_user):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company.is_active = False
    db.commit()
    return company

async def create_company( db, company_data, current_user):
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

async def list_companies(db, current_user):
    return db.query(Company).filter(Company.is_active == True).all()


company_service = {
    "get_company": get_company,
    "update_company": update_company,
    "delete_company": delete_company,
    "create_company": create_company,
    "list_companies": list_companies,
}

    

    