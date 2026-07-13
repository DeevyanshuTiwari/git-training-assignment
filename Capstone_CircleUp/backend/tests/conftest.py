import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base
from app.db.dependencies import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.models.activity import Activity
from app.models.participation import Participation

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


@pytest.fixture
def create_test_user(db_session):
    def _create_user(email="test@test.com", name="Test User"):
        from app.core.security import hash_password
        user = User(
            email=email,
            name=name,
            password=hash_password("Password@123"),
            phone_number="9876543210",
            city="Indore",
            bio="Bio"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def user_token(create_test_user):
    user = create_test_user()
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
