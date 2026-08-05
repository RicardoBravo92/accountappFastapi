from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.contacts import contact_service

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    company_id: int = Query(...),
    type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await contact_service["list_contacts"](db, company_id, type, current_user)

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await contact_service["create_contact"](db, contact_data, current_user)

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await contact_service["get_contact"](db, contact_id, current_user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await contact_service["update_contact"](db, contact_id, contact_data, current_user)

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await contact_service["delete_contact"](db, contact_id, current_user)
