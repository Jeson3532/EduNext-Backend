from src.database.methods import BadgeMethods
from src.database.responses import FailedResponse
from src.badges.achievments import Achievement
import asyncio
from src.badges.status import BadgeScanStatus
from src.badges.rules import BadgeRules


class BadgeDispatcher:
    def __init__(self, user_id):
        self.user_id = user_id

    @staticmethod
    async def check_rule(achievement, total_badges):
        if isinstance(achievement, Achievement):
            response = await BadgeMethods.give(achievement)
            if isinstance(response, FailedResponse):
                total_badges[achievement.achievement_name] = BadgeScanStatus.FAILED, response.detail
            else:
                total_badges[achievement.achievement_name] = BadgeScanStatus.SUCCESS
        else:
            total_badges[achievement] = BadgeScanStatus.NO_SUCCESS

    async def scan(self):
        total_badges = dict()
        # Проверка всех достижений
        await self.check_rule(await BadgeRules.first_rule(user_id=self.user_id), total_badges)
        await self.check_rule(await BadgeRules.second_rule(user_id=self.user_id), total_badges)
        return total_badges



