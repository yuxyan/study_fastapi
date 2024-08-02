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
    for user in user_list:
        if user.username == form_data.username and user.password == crud.encode_password(form_data.password):
            return {"access_token": form_data.username, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.post("/create_user/")
async def create_user(username: str = Form(max_length=50), password: str = Form(max_length=50),
                      uid: int = Form(), db: Session = Depends(get_db)):
    user = schema.UserIn(uid=uid, username=username, password=password)
    db_user = crud.get_user_id(db, uid=user.uid)
    if db_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    crud.create_user(db, user)
    return crud.get_user_id(db, uid=user.uid)


@app.post("/create_household/")
async def create_household(building_num: str = Form(max_length=4), room_num: str = Form(max_length=4),
                           area: int = Form(gt=0), telephone: str | None = None,
                           person_name: str | None = None, work_unit: str | None = None,
                           home_num: int | None = None, weixiu_money: int | None = None,
                           db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    if current_user.privilege != "ROOT":
        raise HTTPException(status_code=403, detail="没有权限")
    db_household = crud.get_household(db, building_num, room_num)
    if db_household is not None:
        raise HTTPException(status_code=400, detail="已存在")

    if person_name is not None:
        is_person = "True"
    else:
        is_person = "False"
    household = schema.HouseholdInfo(building_number=building_num, room_number=room_num, area=area, is_person=is_person,
                                     telephone_number=telephone, person_name=person_name, work_unit=work_unit,
                                     home_number=home_num, weixiu_money=weixiu_money)
    return crud.create_household(db, household)


@app.post("/search_household/")
async def search_household(building_num: str = Form(max_length=4), room_num: str = Form(max_length=4),
                           db: Session = Depends(get_db), current_user: schema.User = Depends(get_current_user)):
    db_household = crud.get_household(db, building_num, room_num)
    if db_household is None:
        raise HTTPException(status_code=404, detail="找不到")
    if current_user.privilege == "ROOT":
        return db_household
    else:
        if db_household.person_name is not None:
            is_person = "True"
        else:
            is_person = "False"
        household_info = schema.Household(building_number=db_household.building_number, room_number=db_household.room_number,
                                          area=db_household.area, is_person=is_person)
        return household_info


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
async def update_user_root(update_user_uid: int = Form(), new_privilege: str = Form(max_length=50), db: Session = Depends(get_db),
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
