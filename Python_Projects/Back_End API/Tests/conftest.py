import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from App.Main import app
from App.Database import Base, get_db
from App.Models.User import User, RoleEnum
from App.Auth.Password import hash_password

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def admin_token(client):
    # Create admin directly in DB (self-registration as admin is blocked by design)
    db = TestingSession()
    admin = User(email="admin@test.com", hashed_password=hash_password("adminpass"), role=RoleEnum.admin)
    db.add(admin)
    db.commit()
    db.close()
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    return res.json()["access_token"]

@pytest.fixture(scope="function")
def student_token(client):
    client.post("/auth/register", json={"email": "student@test.com", "password": "studentpass", "role": "student"})
    res = client.post("/auth/login", json={"email": "student@test.com", "password": "studentpass"})
    return res.json()["access_token"]

@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}

@pytest.fixture(scope="function")
def created_student(client, admin_headers):
    res = client.post("/students/", json={
        "full_name": "Test Student", "email": "tstudent@example.com",
        "password": "tstudentpass", "department": "CS", "gpa": 3.5,
    }, headers=admin_headers)
    return res.json()
