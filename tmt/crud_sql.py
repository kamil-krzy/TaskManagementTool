from sqlmodel import Session, select

from .crud_base import ProjectOperations, TaskOperations
from .models import Project, ProjectBase, ProjectUpdate, Task, TaskBase, TaskUpdate


class SQLProjectOperations(ProjectOperations):
    def __init__(self, session: Session):
        self._session = session

    def get_projects_count(self) -> int:
        return len(self._session.exec(select(Project)).all())

    def get_projects(self, offset: int, limit: int) -> list[Project]:
        projects = self._session.exec(select(Project).offset(offset).limit(limit)).all()
        return projects

    def get_project_by_id(self, _id: int) -> Project:
        return self._session.get(Project, _id)

    def create_project(self, project: Project) -> Project:
        self._session.add(project)
        self._session.commit()
        self._session.refresh(project)
        return project

    def update_project(self, project: Project) -> Project:
        self._session.add(project)
        self._session.commit()
        self._session.refresh(project)
        return project

    def delete_project(self, project: Project) -> None:
        self._session.delete(project)
        self._session.commit()

    @staticmethod
    def apply_update(project: Project, project_update: ProjectUpdate) -> Project:
        project_data = project_update.model_dump(exclude_unset=True)
        project.sqlmodel_update(project_data)

        return project

    @staticmethod
    def get_db_project_object( project: ProjectBase):
        return Project(title=project.title, deadline=project.deadline) # ensure type validation

class SQLTaskOperations(TaskOperations):
    def __init__(self, session: Session):
        self._session = session

    def get_tasks_count(self) -> int:
        return len(self._session.exec(select(Task)).all())

    def get_task_by_id(self, _id: int) -> Task:
        return self._session.get(Task, _id)

    def get_tasks_by_project_id_except_ids(self, project_id: int, task_ids: list[int]) -> list[Task]:
        return self._session.exec(select(Task).where(Task.project_id == project_id, Task.id.not_in(task_ids))).all()

    def get_tasks(self, offset: int, limit: int) -> list[Task]:
        tasks = self._session.exec(select(Task).offset(offset).limit(limit)).all()
        return tasks

    def get_tasks_with_deadlines(self) -> list[Task]:
        tasks = self._session.exec(select(Task).where(Task.deadline != None))
        return tasks

    def create_task(self, task: Task) -> Task:
        self._session.add(task)
        self._session.commit()
        self._session.refresh(task)
        return task

    def update_task(self, task: Task) -> Task:
        self._session.add(task)
        self._session.commit()
        self._session.refresh(task)
        return task

    def delete_task(self, task: Task) -> None:
        self._session.delete(task)
        self._session.commit()

    @staticmethod
    def apply_update(task: Task, task_update: TaskUpdate) -> Task:
        task_data = task_update.model_dump(exclude_unset=True)
        task.sqlmodel_update(task_data)
        return task

    @staticmethod
    def create_db_task_object(task: TaskBase) -> Task:
        return Task(title=task.title, desc=task.desc, deadline=task.deadline,
                    completed=task.completed, project_id=task.project_id) # ensure type validation