from pydantic import BaseModel


class User(BaseModel):
    uid: int
    username: str
    privilege: str | None = None


class UserIn(User):
    password: str


class Household(BaseModel):
    building_number: str
    room_number: str
    area: int = 100
    is_person: str = "False"


class HouseholdInfo(Household):
    telephone_number: str | None = None
    person_name: str | None = None
    work_unit: str | None = None
    home_number: int | None = None
    weixiu_money: int | None = None
