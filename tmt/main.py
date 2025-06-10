from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Session

from .crud_sql import SQLProjectOperations, SQLTaskOperations
from .models import Project, ProjectBase, ProjectRead, ProjectUpdate, Task, TaskBase, TaskRead, TaskUpdate
from .database import get_sqlite_db, create_db
from .services import ProjectService, TaskService


SQLiteSessionDep = Annotated[Session, Depends(get_sqlite_db)]

def get_project_service(session: SQLiteSessionDep) -> ProjectService:
    project_ops = SQLProjectOperations(session)
    task_ops = SQLTaskOperations(session)
    return ProjectService(project_ops, task_ops)

def get_task_service(session: SQLiteSessionDep) -> TaskService:
    task_ops = SQLTaskOperations(session)
    project_ops = SQLProjectOperations(session)
    return TaskService(task_ops, project_ops)

ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]

tmt = FastAPI()


@tmt.on_event("startup")
def on_startup():
    create_db()


### TASKS


@tmt.get("/tasks", response_model=list[TaskRead], status_code=200)
def get_tasks(task_service: TaskServiceDep, limit: Annotated[int, Query(le=100)] = 100, offset: int = 0) -> list[Task]:
    try:
        return task_service.get_paginated_tasks(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@tmt.get("/tasks/deadlines", response_model=list[TaskRead], status_code=200)
def get_tasks_with_deadline(task_service: TaskServiceDep) -> list[Task]:
    try:
        return task_service.get_tasks_with_deadline()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task: TaskBase, task_service: TaskServiceDep) -> Task:
    try:
        return task_service.create_task(task=task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.put("/tasks/{_id}", response_model=TaskRead, status_code=200)
def update_task(_id: int, task_update: TaskUpdate, task_service: TaskServiceDep) -> Task:
    try:
        return task_service.update_task(task_id=_id, task_update=task_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.delete("/tasks/{_id}", status_code=204)
def delete_task(_id: int, task_service: TaskServiceDep) -> None:
    try:
        task_service.delete_task(task_id=_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


### PROJECTS


@tmt.get("/projects", response_model=list[ProjectRead], status_code=200)
def get_projects(project_service: ProjectServiceDep, limit: Annotated[int, Query(le=100)] = 100, offset: int = 0) -> list[Project]:
    try:
        return project_service.get_paginated_projects(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(project: ProjectBase, project_service: ProjectServiceDep) -> Project:
    try:
        return project_service.create_project(project=project)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.put("/projects/{_id}", response_model=ProjectRead, status_code=200)
def update_project(_id: int, project_update: ProjectUpdate, project_service: ProjectServiceDep) -> Project:
    try:
        return project_service.update_project(project_id=_id, project_update=project_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@tmt.delete("/projects/{_id}", status_code=204)
def delete_project(_id: int, project_service: ProjectServiceDep) -> None:
    try:
        project_service.delete_project(project_id=_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
