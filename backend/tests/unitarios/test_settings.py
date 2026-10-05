from app.configuracion.settings import Settings


def test_special_characters_in_password_are_preserved():
    settings = Settings(_env_file=None, db_password="test@:/#%value", database_url="")
    assert settings.get_database_url().password == "test@:/#%value"
    assert "test@:/#%value" not in repr(settings)


def test_postgres_url_uses_psycopg():
    settings = Settings(_env_file=None, database_url="postgresql://user:pass@localhost/test")
    assert settings.get_database_url().drivername == "postgresql+psycopg"
