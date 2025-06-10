from datetime import date
from sqlmodel import Field, Session, SQLModel, select, Relationship


class ProjectBase(SQLModel):
    title: str
    deadline: date

    def is_deadline_valid(self) -> bool:
        """Ensure deadline is not in the past."""
        if self.deadline and self.deadline < date.today():
            return False
        return True

    def are_required_filled(self):
        return self.title and self.deadline

class ProjectRead(ProjectBase):
    id: int | None = Field(default=None, primary_key=True)
    title: str | None = None
    deadline: date | None = None
    tasks: list["Task"] | None = None


class ProjectUpdate(ProjectBase):
    title: str | None = None
    deadline: date | None = None
    tasks_ids: list[int] | None = None


class Project(ProjectBase, table=True):
    id: int = Field(default=None, primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="project")


class TaskBase(SQLModel):
    title: str
    desc: str
    deadline: date | None = Field(default=None, index=True)
    completed: bool = Field(default=False)
    project_id: int | None = Field(default=None, foreign_key="project.id", index=True, nullable=True)

    def is_deadline_valid(self) -> bool:
        """Ensure deadline is not in the past."""
        if self.deadline and self.deadline < date.today():
            return False
        return True

    def are_required_filled(self):
        return self.title and self.desc

class TaskRead(TaskBase):
    id: int | None = Field(default=None, primary_key=True)
    deadline: date | None = None
    project: Project | None = None


class TaskUpdate(TaskBase):
    title: str | None = None
    desc: str | None = None
    completed: bool | None = None


class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)

    project: Project | None = Relationship(back_populates="tasks")
