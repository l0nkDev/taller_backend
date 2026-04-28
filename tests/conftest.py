import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from main import app
from database import get_session

sqlite_url = "sqlite://"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session_override] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()