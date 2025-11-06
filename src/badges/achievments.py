from pydantic import BaseModel


class Achievement(BaseModel):
    achievement_name: str
    user_id: int
    badge_id: int
