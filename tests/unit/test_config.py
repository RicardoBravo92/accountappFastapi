from app.config import settings


def test_settings():
    assert settings.APP_NAME == "accountapp"
    assert settings.DEBUG is True
    assert settings.DATABASE_URL.startswith("postgresql://")
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert "http://localhost:3000" in settings.CORS_ORIGINS
