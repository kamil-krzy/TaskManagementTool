from sqlmodel import create_engine, Session, SQLModel

# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./db/task_management_tool.sqlite"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def get_sqlite_db():
    with Session(engine) as session:
        yield session

def create_db():
    SQLModel.metadata.create_all(engine)

