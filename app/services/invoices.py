
from app.models import Invoice
from app.models.invoice import InvoiceStatus
from fastapi import HTTPException
async def list_invoices(db, company_id, current_user):
    return db.query(Invoice).filter(Invoice.company_id == company_id).all()

async def create_invoice(db, invoice_data, current_user):
    invoice = Invoice(
        company_id=invoice_data.company_id,
        customer_id=invoice_data.customer_id,
        invoice_number=invoice_data.invoice_number,
        status=InvoiceStatus.DRAFT,
        issue_date=invoice_data.issue_date,
        due_date=invoice_data.due_date,
        currency_code=invoice_data.currency_code,
        notes=invoice_data.notes,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

async def get_invoice(db, invoice_id, current_user):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

async def update_invoice(db, invoice_id, invoice_data, current_user):
    invoice = get_invoice(db, invoice_id, current_user)
    update_data = invoice_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)
    db.commit()
    db.refresh(invoice)
    return invoice

async def delete_invoice(db, invoice_id, current_user):
    invoice = get_invoice(db, invoice_id, current_user)
    db.delete(invoice)
    db.commit()
    return invoice


invoice_service = {
    "list_invoices": list_invoices,
    "create_invoice": create_invoice,
    "get_invoice": get_invoice,
    "update_invoice": update_invoice,
    "delete_invoice": delete_invoice,
}
