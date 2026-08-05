
from fastapi import HTTPException
from app.models.tax import Tax
async def list_taxes(db, company_id, current_user):
    return db.query(Tax).filter(Tax.company_id == company_id).all()

async def create_tax(db, tax_data, current_user):
    tax = Tax(**tax_data.model_dump())
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax

async def get_tax(db, tax_id, current_user):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")
    return tax

async def update_tax(db, tax_id, tax_data, current_user):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")
    update_data = tax_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tax, key, value)
    db.commit()
    db.refresh(tax)
    return tax

async def delete_tax(db, tax_id, current_user):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")
    tax.is_active = False
    db.commit()


tax_service = {
    "list_taxes": list_taxes,
    "create_tax": create_tax,
    "get_tax": get_tax,
    "update_tax": update_tax,
    "delete_tax": delete_tax,
}