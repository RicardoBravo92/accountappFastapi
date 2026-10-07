from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    CONTACT_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.contacts import (
    list_contacts,
    create_contact,
    get_contact,
    update_contact,
    delete_contact,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=list[ContactResponse])
def list_contacts_endpoint(
    company_id: int = Query(...),
    type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CONTACT_PERMISSIONS["list"])),
):
    return list_contacts(db, company_id, type, current_user)

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact_endpoint(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CONTACT_PERMISSIONS["create"])),
):
    return create_contact(db, contact_data, current_user)

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact_endpoint(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CONTACT_PERMISSIONS["read"])),
):
    return get_contact(db, contact_id, current_user)

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact_endpoint(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CONTACT_PERMISSIONS["update"])),
):
    return update_contact(db, contact_id, contact_data, current_user)

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact_endpoint(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CONTACT_PERMISSIONS["delete"])),
):
    delete_contact(db, contact_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
