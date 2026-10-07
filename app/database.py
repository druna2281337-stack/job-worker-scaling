from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://jobflow:jobflow@postgres:5432/jobflow"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def init_db():
    from app.models import Job
    Base.metadata.create_all(bind=engine)
