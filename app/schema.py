from pydantic import BaseModel


class User(BaseModel):
    uid: int
    name: str
    privilege: str | None = None


class UserIn(User):
    password: str
