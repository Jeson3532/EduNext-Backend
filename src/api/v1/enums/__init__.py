from enum import StrEnum


class Roles(StrEnum):
    USER = "Пользователь"
    ADMIN = "Администратор"


class LessonTypes(StrEnum):
    PRACTICAL = "Практическая"
    LECTURE = "Лекционная"


class MaterialTypes(StrEnum):
    COURSE = "Курс"
    LECTURE = "Урок"


class ProgressTypes(StrEnum):
    PROGRESS = "В процессе"
    COMPLETED = "Завершен"
