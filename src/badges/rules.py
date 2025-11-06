from src.database.methods import UserMethods
from src.database.responses import FailedResponse
from src.database.model import Users
from src.badges.achievments import Achievement
from typing import Union


class BadgeRules:
    @staticmethod
    async def first_rule(user_id) -> Union[str, Achievement]:
        achievement_name = "Всемогущий"
        response = await UserMethods.get_user(user_id)
        if isinstance(response, FailedResponse):
            return achievement_name
        user: Users = response.data
        success_in_a_row = user.success_in_a_row
        if success_in_a_row >= 10:
            return Achievement(user_id=user_id, badge_id=1, achievement_name=achievement_name)
        return achievement_name

    @staticmethod
    async def second_rule(user_id) -> Union[str, Achievement]:
        achievement_name = "Все с чего-то начинали"
        response = await UserMethods.get_user(user_id)
        if isinstance(response, FailedResponse):
            return achievement_name
        user: Users = response.data
        success_in_a_row = user.success_in_a_row
        if success_in_a_row >= 1:
            return Achievement(user_id=user_id, badge_id=2, achievement_name=achievement_name)
        return achievement_name
