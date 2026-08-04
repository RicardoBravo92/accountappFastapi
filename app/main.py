from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
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


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(companies_router)
    app.include_router(contacts_router)
    app.include_router(accounts_router)
    app.include_router(transactions_router)
    app.include_router(invoices_router)
    app.include_router(bills_router)
    app.include_router(items_router)
    app.include_router(categories_router)
    app.include_router(taxes_router)
    app.include_router(currencies_router)
    app.include_router(reports_router)

    Base.metadata.create_all(bind=engine)

    return app


app = create_app()


@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}