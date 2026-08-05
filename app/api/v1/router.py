from fastapi import APIRouter

api_router = APIRouter()

from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.accounts import router as accounts_router
from app.api.transactions import router as transactions_router
from app.api.transfers import router as transfers_router
from app.api.invoices import router as invoices_router
from app.api.bills import router as bills_router
from app.api.items import router as items_router
from app.api.categories import router as categories_router
from app.api.taxes import router as taxes_router
from app.api.currencies import router as currencies_router
from app.api.reports import router as reports_router
from app.api.uploads import router as uploads_router

api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(contacts_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(invoices_router)
api_router.include_router(bills_router)
api_router.include_router(items_router)
api_router.include_router(categories_router)
api_router.include_router(taxes_router)
api_router.include_router(currencies_router)
api_router.include_router(transfers_router)
api_router.include_router(reports_router)
api_router.include_router(uploads_router)
