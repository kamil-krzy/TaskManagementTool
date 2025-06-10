from abc import ABC, abstractmethod
from .models import Project, ProjectBase, ProjectRead, ProjectUpdate, Task, TaskBase, TaskUpdate, TaskRead

class ProjectOperations(ABC):
    @abstractmethod
    def get_projects_count(self) -> int:
        pass

    @abstractmethod
    def get_projects(self, offset: int, limit: int) -> list[Project]:
        pass

    @abstractmethod
    def get_project_by_id(self, _id: int) -> Project:
        pass

    @abstractmethod
    def create_project(self, project: ProjectBase) -> Project:
        pass

    @abstractmethod
    def update_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    def delete_project(self, project: Project) -> None:
        pass

    @staticmethod
    @abstractmethod
    def apply_update(project: Project, project_update: ProjectUpdate) -> Project:
        """ Apply changes from ProjectUpdate model to Project and return Project object with changes."""
        pass

class TaskOperations(ABC):
    @abstractmethod
    def get_tasks_count(self) -> int:
        pass

    @abstractmethod
    def get_task_by_id(self, _id: int) -> Task:
        pass

    @abstractmethod
    def get_tasks(self, offset: int, limit: int) -> list[Task]:
        pass

    @abstractmethod
    def get_tasks_with_deadlines(self) -> list[Task]:
        pass

    @abstractmethod
    def create_task(self, task: Task) -> Task:
        pass

    @abstractmethod
    def update_task(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete_task(self, task: Task) -> None:
        pass

    @staticmethod
    @abstractmethod
    def apply_update(task: Task, task_update: TaskUpdate) -> Task:
        """ Apply changes from TaskUpdate model to Task and return Task object with changes."""
        pass