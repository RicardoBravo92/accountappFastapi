"""Database seed script for AccountApp backend.

Follows the same pattern as akaunting:
1. Company (main entity)
2. Accounts (default cash account)
3. Categories (income, expense, banking defaults)
4. Currencies (default USD)

Usage:
    uv run python scripts/seed.py              # Seed if empty
    uv run python scripts/seed.py --fresh      # Delete all and reseed
"""

import sys
import os
import argparse


def seed_database(fresh=False):
    """Seed the database with initial data."""
    # Import models FIRST to register them with Base
    from app.core.auth import hash_password
    from app.models.auth.user import User, UserRole
    from app.models.company import Company
    from app.models.account import Account, AccountType
    from app.models.category import Category, CategoryType
    from app.models.currency import Currency
    from app.models.contact import Contact

    # Import database configuration AFTER models are imported
    from app.core.database import Base, engine, SessionLocal
    
    # Create tables (models now registered with Base)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Optionally clear existing data
        if fresh:
            print("Clearing existing data...")
            try:
                for table in reversed(Base.metadata.sorted_tables):
                    db.execute(table.delete())
                db.commit()
            except Exception:
                db.rollback()
                print("Could not clear data. Database may be empty.")

        # Check if data already exists
        if db.query(Company).first() and not fresh:
            print("Database already has data. Use --fresh to reset.")
            return

        # 1. Create Company (mirrors akaunting Company.php)
        print("Creating company...")
        company = Company(
            name="Demo Company",
            slug="demo-company",
            email="demo@example.com",
            phone="506-1234-5678",
            currency_code="USD",
            is_active=True,
        )
        db.add(company)
        db.flush()  # Get company ID without committing

        # 2. Create User (mirrors akaunting User.php + dashboards)
        print("Creating admin user...")
        admin_user = User(
            email="admin@demo.com",
            username="admin",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

        # 3. Create Accounts (mirrors akaunting Accounts.php)
        print("Creating default accounts...")
        default_accounts = [
            {
                "code": "1000",
                "name": "Cash",
                "type": AccountType.ASSET,
                "is_bank": False,
            },
            {
                "code": "1001",
                "name": "Bank Account",
                "type": AccountType.ASSET,
                "is_bank": True,
            },
            {
                "code": "5000",
                "name": "General Expenses",
                "type": AccountType.EXPENSE,
                "is_bank": False,
            },
        ]

        for acc in default_accounts:
            account = Account(
                company_id=company.id,
                code=acc["code"],
                name=acc["name"],
                type=acc["type"],
                is_bank=acc["is_bank"],
                is_active=True,
            )
            db.add(account)
            db.flush()

        # 4. Create Categories (mirrors akaunting Categories.php)
        print("Creating default categories...")
        categories = [
            {"name": "Transfer", "type": CategoryType.BANKING, "color": "#3c3f72"},
            {"name": "Deposit", "type": CategoryType.INCOME, "color": "#efad32"},
            {"name": "Sales", "type": CategoryType.INCOME, "color": "#6da252"},
            {"name": "Expense", "type": CategoryType.EXPENSE, "color": "#e5e5e5"},
            {"name": "General", "type": CategoryType.PRODUCT, "color": "#328aef"},
            {"name": "Cost of Goods Sold", "type": CategoryType.EXPENSE, "color": "#ef3281"},
        ]

        for cat_data in categories:
            category = Category(
                company_id=company.id,
                name=cat_data["name"],
                type=cat_data["type"],
                color=cat_data["color"],
                is_active=True,
            )
            db.add(category)
            db.flush()

        # 5. Create Currency (mirrors akaunting Currencies.php)
        print("Creating currencies...")
        usd_currency = Currency(
            company_id=company.id,
            code="USD",
            name="US Dollar",
            symbol="$",
            exchange_rate=1.0,
            is_base=True,
            is_active=True,
        )
        db.add(usd_currency)

        # 6. Create Sample Contact (mirrors akaunting test data)
        print("Creating sample contacts...")
        contact = Contact(
            company_id=company.id,
            type="customer",
            name="Sample Customer",
            email="customer@sample.com",
            phone="506-9876-5432",
            is_active=True,
        )
        db.add(contact)

        # Commit all changes
        db.commit()
        print("Seeded database successfully!")
        print(f"  Company: {company.name} (ID: {company.id})")
        print(f"  Admin User: admin@demo.com / admin123")
        print(f"  Accounts: {db.query(Account).count()}")
        print(f"  Categories: {db.query(Category).count()}")
        print(f"  Currencies: {db.query(Currency).count()}")
        print(f"  Contacts: {db.query(Contact).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed AccountApp database")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Delete existing data before seeding",
    )
    args = parser.parse_args()

    print("Seeding AccountApp database...")
    seed_database(fresh=args.fresh)
