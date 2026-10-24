"""Pytest test configuration and fixtures."""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure pure-python SQLAlchemy
os.environ["DISABLE_SQLALCHEMY_C_EXTENSIONS"] = "1"
os.environ["MATHQUEST_ENV"] = "test"
os.environ["MATHQUEST_DATABASE_URL"] = "sqlite:///:memory:"

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app

from sqlalchemy.pool import StaticPool

# Test SQLite in-memory database with StaticPool so all test connections share the same memory DB
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test function."""
    from backend.app.db import models  # noqa: F401
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
