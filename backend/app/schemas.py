from pydantic import BaseModel
from app.models import TitleType

####### Users and authentication #######

class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    user_id: int
    username: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str

class UserDelete(BaseModel):
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


####### Titles #######

class TitleIn(BaseModel):
    tmdb_id: int
    title_type: TitleType
