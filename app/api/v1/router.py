from fastapi import APIRouter

api_router = APIRouter()

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.items import router as items_router
from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.contacts import router as contacts_router
from app.api.v1.endpoints.accounts import router as accounts_router
from app.api.v1.endpoints.transactions import router as transactions_router
from app.api.v1.endpoints.transfers import router as transfers_router
from app.api.v1.endpoints.invoices import router as invoices_router
from app.api.v1.endpoints.bills import router as bills_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.taxes import router as taxes_router
from app.api.v1.endpoints.currencies import router as currencies_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.uploads import router as uploads_router
from app.api.v1.endpoints.webhooks import router as webhooks_router

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(items_router)
api_router.include_router(companies_router)
api_router.include_router(contacts_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(invoices_router)
api_router.include_router(bills_router)
api_router.include_router(categories_router)
api_router.include_router(taxes_router)
api_router.include_router(currencies_router)
api_router.include_router(transfers_router)
api_router.include_router(reports_router)
api_router.include_router(uploads_router)
api_router.include_router(webhooks_router)
