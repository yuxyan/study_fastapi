from fastapi import Depends, FastAPI, HTTPException, Form, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, models, schema
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    print(token)
    user = crud.get_user_name(db, token)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_list = crud.get_all_users(db)
    flag = 0
    for user in user_list:
        if user.username == form_data.username and user.password == crud.encode_password(form_data.password):
            flag = 1
            break
    if flag:
        return {"access_token": form_data.username, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.post("/create_user/")
async def create_user(username: str = Form(), password: str = Form(),
                      uid: int = Form(), db: Session = Depends(get_db)):
    user = schema.UserIn(uid=uid, username=username, password=password)
    db_user = crud.get_user_id(db, uid=user.uid)
    if db_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    crud.create_user(db, user)
    return crud.get_user_id(db, uid=user.uid)


@app.get("/user/{user_uid}")
async def userid(user_uid: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_id(db, uid=user_uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="找不到")
    return db_user


@app.get("/users/me")
async def read_users_me(current_user: schema.User = Depends(get_current_user)):
    return current_user


@app.put("/root_user/update")
async def update_user_root(update_user_uid: int = Form(), new_privilege: str = Form(), db: Session = Depends(get_db),
                           current_user: schema.User = Depends(get_current_user)):
    """
    更新用户权限
    - 需要ROOT
    """
    if current_user.privilege != "ROOT":
        raise HTTPException(status_code=403, detail="没有权限")
    update_user = crud.update_user_privilege(db,  new_privilege, update_user_uid)
    if update_user is None:
        raise HTTPException(status_code=404, detail="找不到")
    else:
        return update_user


@app.put("/user/update")
async def update_user_info(db: Session = Depends(get_db),
                           new_name: str | None = None, new_password: str | None = None,
                           current_user: schema.User = Depends(get_current_user)):
    """
    修改用户名、密码
    """
    db_user = crud.update_user_info(db, current_user.uid, new_name, new_password)
    if db_user is None:
        raise HTTPException(status_code=404, detail="找不到")
    else:
        return db_user
