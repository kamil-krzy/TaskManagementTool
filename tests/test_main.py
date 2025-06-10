from tmt.database import get_sqlite_db
from tmt.main import tmt
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session


# In-memory SQLite database for tests
test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
connection = test_engine.connect()
SQLModel.metadata.create_all(test_engine)

def override_get_sqlite_db():
    with Session(bind=connection) as session:
        yield session

tmt.dependency_overrides[get_sqlite_db] = override_get_sqlite_db

test_client = TestClient(tmt)


def test_create_task():
    res = test_client.post("/tasks", json={"title": "Basic Task", "desc": "Basic Description"}) #10
    assert res.status_code == 201
    res_data = res.json()
    assert res_data["title"] == "Basic Task"
    assert res_data["desc"] == "Basic Description"
    assert not res_data["completed"]
    assert "id" in  res_data

def test_create_project():
    res = test_client.post("/projects", json={"title": "Basic Project", "deadline": "2999-01-02"}) #4
    assert res.status_code == 201
    res_data = res.json()
    assert res_data["title"] == "Basic Project"
    assert res_data["deadline"] == "2999-01-02"
    assert "id" in  res_data

def test_create_deadline_task():
    res = test_client.post("/tasks", json={"title": "Deadline Task", "desc": "Deadline Description",
                                           "deadline": "2999-01-01", "project_id": 1}) #11
    assert res.status_code == 201
    res_data = res.json()
    assert res_data["title"] == "Deadline Task"

def test_get_tasks():
    res = test_client.get("/tasks")
    assert res.status_code == 200
    res_data = res.json()
    assert isinstance(res_data, list)
    assert any(task["title"] == "Basic Task" for task in res_data)
    assert len(res_data) == 2

def test_get_tasks_with_deadlines():
    res = test_client.get("/tasks/deadlines")
    assert res.status_code == 200
    res_data = res.json()
    assert isinstance(res_data, list)
    assert res_data[0]["title"] == "Deadline Task"

def test_update_task():
    res = test_client.put("/tasks/2", json={"title": "Deadline Task Modified", "completed": True})
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["title"] == "Deadline Task Modified"
    assert res_data["desc"] == "Deadline Description"
    assert res_data["completed"]
    assert res_data["id"] == 2
    assert res_data["project"] is not None

def test_invalid_deadline_update_task():
    res = test_client.put("/tasks/2", json={"deadline": "2999-01-03"})
    assert res.status_code == 400
    res_data = res.json()
    assert "2999-01-03" in res_data["detail"]
    assert "2999-01-02" in res_data["detail"]
    assert "deadline" in res_data["detail"]


def test_invalid_project_id_update_task():
    res = test_client.put("/tasks/2", json={"project_id": 5})
    assert res.status_code == 400
    res_data = res.json()
    assert "5" in res_data["detail"]
    assert "non-existent" in res_data["detail"]

def test_delete_task():
    res = test_client.delete("/tasks/1")
    assert res.status_code == 204
