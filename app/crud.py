from sqlalchemy.orm import Session
from . import models, schema


def encode_password(password: str):
    return "加密" + password + "加密"


def get_user_id(db: Session, uid: int):
    return db.query(models.User).filter(models.User.uid == uid).first()


def get_user_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.username == name).first()


def create_user(db: Session, user: schema.UserIn):
    hash_password = encode_password(user.password)
    db_user = models.User(uid=user.uid, username=user.name, password=hash_password, privilege=user.privilege)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session):
    return db.query(models.User).all()


def update_user_privilege(db: Session, new_privilege: str, update_user_uid: int):
    db_user = get_user_id(db, uid=update_user_uid)
    if db_user is None:
        return None
    setattr(db_user, 'privilege', new_privilege)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_info(db: Session, user_uid: int, new_name: str | None = None, new_password: str | None = None):
    db_user = get_user_id(db, uid=user_uid)
    if db_user is None:
        return None
    if new_name is not None:
        setattr(db_user, 'username', new_name)
    if new_password is not None:
        setattr(db_user, 'password', encode_password(new_password))
    db.commit()
    db.refresh(db_user)
    return db_user
