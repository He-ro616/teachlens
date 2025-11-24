from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from flask_login import UserMixin

# -----------------------------
# 1. SQLite Database URL
# -----------------------------
DATABASE_URL = "sqlite:///./teachlens.db"

# -----------------------------
# 2. Engine & Session
# -----------------------------
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# 3. Base
# -----------------------------
Base = declarative_base()

# -----------------------------
# 4. Teacher Model
# -----------------------------
class Teacher(UserMixin, Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    education_details = Column(Text, nullable=True)

    reports = relationship("Report", back_populates="teacher")

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Teacher(id='{self.id}', email='{self.email}')>"

# -----------------------------
# 5. Report Model
# -----------------------------
class Report(Base):
    __tablename__ = 'reports'

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rubric = Column(JSON, nullable=False)
    transcript = Column(Text, nullable=False)
    pdf_data = Column(LargeBinary, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))

    teacher = relationship("Teacher", back_populates="reports")

    def __repr__(self):
        return f"<Report(id='{self.id}', filename='{self.filename}', timestamp='{self.timestamp}')>"

# -----------------------------
# 6. Init DB
# -----------------------------
def init_db():
    Base.metadata.create_all(bind=engine)

# -----------------------------
# 7. DB Generator
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
