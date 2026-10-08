from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# 1. Konfigurasi Database SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Model Tabel Database
class TodoModel(Base):
    __tablename__ = "todos"
    priority = Column(String, default="low")
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# 3. Skema Data (Pydantic)
class TodoCreate(BaseModel):
    title: str
    priority: str = "low"

class TodoResponse(BaseModel):
    priority: str = "low"
    id: int
    title: str
    completed: bool

    class Config:
        from_attributes = True

# 4. Inisialisasi FastAPI & Dependency DB
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Endpoint CRUD

# GET: Ambil semua todo
@app.get("/api/todos", response_model=List[TodoResponse])
def read_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()

# POST: Tambah todo baru
@app.post("/api/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(title=todo.title, priority=todo.priority)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# PUT: Update status todo (selesai / belum)
@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo tidak ditemukan")
    db_todo.completed = not db_todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

# DELETE: Hapus todo
@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo tidak ditemukan")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo berhasil dihapus"}