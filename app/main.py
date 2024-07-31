from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schema
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create_user/")
async def create_user(user: schema.UserIn, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, uid=user.uid)
    if db_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    crud.create_user(db, user)
    return crud.get_user(db, uid=user.uid)


@app.get("/login/{user_uid}")
async def login(user_uid: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, uid=user_uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
