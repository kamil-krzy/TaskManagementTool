from .crud_sql import SQLProjectOperations, SQLTaskOperations
from .models import Project, ProjectBase, ProjectUpdate, Task, TaskBase, TaskUpdate

import logging

log = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, project_ops: SQLProjectOperations, task_ops: SQLTaskOperations):
        self._task_ops = task_ops
        self._project_ops = project_ops

    def get_paginated_projects(self, limit: int, offset: int) -> list[Project]:
        total_projects = self._project_ops.get_projects_count()
        if offset > total_projects:
            raise ValueError(f"Offset {offset} exceeds total number of projects {total_projects}.")
        return self._project_ops.get_projects(limit=limit, offset=offset)

    def create_project(self, project: ProjectBase) -> Project:
        db_project = self._project_ops.get_db_project_object(project)
        self.verify_project_before_posting(db_project)
        return self._project_ops.create_project(db_project)

    def delete_project(self, project_id: int) -> None:
        project = self._project_ops.get_project_by_id(project_id)

        if project.tasks:
            # TODO: prevent this or stay with log?
            log.warning(f"Removing project {project_id} that has tasks associated {project.tasks}")
        return self._project_ops.delete_project(project)

    def update_project(self, project_id: int, project_update: ProjectUpdate) -> Project:
        project = self._project_ops.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project with id {project_id} does not exist.")

        project = self._project_ops.apply_update(project=project, project_update=project_update)

        self.verify_project_before_posting(project)

        if project_update.tasks_ids is not None:
            tasks = self._task_ops.get_tasks_by_project_id_except_ids(project_id, project_update.tasks_ids)

            # remove connection from previously assigned tasks
            for task in tasks:
                task.project_id = None
                self._task_ops.update_task(task)

            for task_id in project_update.tasks_ids:
                task = self._task_ops.get_task_by_id(task_id)

                if not task:
                    # can't stop here as it can lead to updating data only partially
                    log.warning(f"Provided task_id {task_id} points to non-existent task.")
                    continue
                task.project_id = project_id
                self._task_ops.update_task(task)


        return self._project_ops.update_project(project=project)

    @staticmethod
    def verify_project_before_posting(project: Project) -> None:
        """Ensure project's deadline is valid and required fields are filled."""
        if not project.is_deadline_valid():
            raise ValueError(f"New deadline {project.deadline} is in the past.")

        if not project.are_required_filled():
            raise ValueError(f"Make sure title and deadline are not null / empty.")

        if project.tasks is not None:
            tasks_with_longer_deadline = [_task.title for _task in project.tasks if project.deadline < _task.deadline]
            if any(tasks_with_longer_deadline):
                raise ValueError(f"Provided deadline {project.deadline} is shorter than deadline for tasks "
                                 f"{tasks_with_longer_deadline}.")


class TaskService:
    def __init__(self, task_ops: SQLTaskOperations, project_ops: SQLProjectOperations):
        self._task_ops = task_ops
        self._project_ops = project_ops

    def get_paginated_tasks(self, limit: int, offset: int) -> list[Task]:
        total_tasks = self._task_ops.get_tasks_count()
        if offset > total_tasks:
            raise ValueError(f"Offset {offset} exceeds total number of tasks {total_tasks}.")
        return self._task_ops.get_tasks(limit=limit, offset=offset)

    def get_tasks_with_deadline(self) -> list[Task]:
        return self._task_ops.get_tasks_with_deadlines()

    def create_task(self, task: TaskBase) -> Task:
        db_task = self._task_ops.create_db_task_object(task)
        self.verify_task_before_posting(db_task)
        return self._task_ops.create_task(db_task)

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        task = self._task_ops.get_task_by_id(task_id)

        if not task:
            raise ValueError(f"Task with id {task_id} does not exist.")

        task = self._task_ops.apply_update(task=task, task_update=task_update)

        self.verify_task_before_posting(task)

        return self._task_ops.update_task(task=task)

    def delete_task(self, task_id: int) -> None:
        task = self._task_ops.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} does not exist.")

        if task.project:
            # TODO: prevent this, add 'deleted' field in Task for 'safe delete' or stay with log?
            log.warning(f"Deleting task {task_id} that is connected to project {task.project_id}")
        return self._task_ops.delete_task(task)

    def verify_task_before_posting(self, task: Task) -> None:
        """Ensure task's deadline is valid, required fields are filled and project_id is correct."""
        if not task.is_deadline_valid():
            raise ValueError(f"Provided deadline is in the past.")
        if not task.are_required_filled():
            raise ValueError(f"Make sure title and description are not null / empty.")

        if task.project_id is not None:
            project = self._project_ops.get_project_by_id(task.project_id)
            if not project:
                raise ValueError(f"Provided project id {task.project_id} points to non-existent project.")

            if task.deadline and project.deadline < task.deadline:
                raise ValueError(f"Provided deadline {task.deadline} is longer than projects deadline {project.deadline}.")