from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///students.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column("Фамилия", String(100), nullable=False, index=True)
    first_name = Column("Имя", String(100), nullable=False)
    faculty = Column("Факультет", String(50), nullable=False)
    subject = Column("Курс", String(100), nullable=False)
    grade = Column("Оценка", Integer, nullable=False)