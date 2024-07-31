from sqlalchemy.orm import Session
from . import models, schema


def encode_password(password: str):
    return "加密" + password + "加密"


def get_user(db: Session, uid: int):
    return db.query(models.User).filter(models.User.uid == uid).first()


def create_user(db: Session, user: schema.UserIn):
    hash_password = encode_password(user.password)
    db_user = models.User(uid=user.uid, username=user.name, password=hash_password, privilege=user.privilege)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
