from app.core.config import settings


def test_settings():
    assert settings.APP_NAME == "accountapp"
    assert settings.ENVIRONMENT in ["production", "development", "test"]
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert settings.API_V1_STR == "/api/v1"
    assert settings.UPLOAD_DIR == "uploads"
    assert settings.MAX_UPLOAD_SIZE > 0
