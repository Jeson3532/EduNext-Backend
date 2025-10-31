from pydantic import BaseModel
from src.api.v1.examples import auth_examples


class UserResponse(BaseModel):
    username: str
    user_id: int
