from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.database.config import DBConfig
from dotenv import load_dotenv
from src.utils.logger import logger

load_dotenv()

# Объект класса с конфигурацией
db_config = DBConfig()

# Данные для подключения
user = db_config.USER
password = db_config.PASSWORD
host = db_config.HOST
port = db_config.PORT
dbname = db_config.DBNAME

engine = create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}", pool_pre_ping=True)
session_maker = async_sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    ...


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Айди в системе")
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False, comment="Хешированный пароль пользователя")
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True, nullable=True)
    role: Mapped[str] = mapped_column(comment="Роль участника в системе")

    @classmethod
    async def create_table(cls):
        async with engine.begin() as connect:
            logger.info(f"Создаю базу данных {cls.__tablename__}...")
            await connect.run_sync(
                lambda sync_conn: cls.metadata.drop_all(sync_conn, tables=[cls.__table__])
            )
            await connect.run_sync(
                lambda sync_conn: cls.metadata.create_all(sync_conn, tables=[cls.__table__])
            )
            logger.info("База данных создана!")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Айди в системе")
    course_title: Mapped[str] = mapped_column(nullable=False, comment='Название курса')
    author: Mapped[str] = mapped_column(nullable=False, comment="Автор курса")
    desc: Mapped[str] = mapped_column(nullable=True, comment="Описание курса")
    course_categories: Mapped[str] = mapped_column(nullable=False, comment="Категории курса")
    course_num_peoples: Mapped[int] = mapped_column(default=0, nullable=False,
                                                    comment="Количество людей, записанных на курс")
    num_lessons: Mapped[int] = mapped_column(nullable=False, comment="Количество уроков в курсе")

    @classmethod
    async def create_table(cls):
        async with engine.begin() as connect:
            logger.info(f"Создаю базу данных {cls.__tablename__}...")
            await connect.run_sync(
                lambda sync_conn: cls.metadata.drop_all(sync_conn, tables=[cls.__table__])
            )
            await connect.run_sync(
                lambda sync_conn: cls.metadata.create_all(sync_conn, tables=[cls.__table__])
            )
            logger.info("База данных создана!")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Айди в системе")
    course_name: Mapped[str] = mapped_column(nullable=False, comment='Название курса, к которому относится урок')
    lesson_title: Mapped[str] = mapped_column(nullable=False, comment='Название урока')
    desc: Mapped[str] = mapped_column(nullable=True, comment="Описание урока")
    lesson_num_success_peoples: Mapped[int] = mapped_column(default=0, nullable=False,
                                                            comment="Количество людей, прошедших урок.")
    level: Mapped[int] = mapped_column(nullable=False, comment="Уровень сложности задания")
    pos: Mapped[int] = mapped_column(nullable=False, comment='Позиция урока в курсе')

    @classmethod
    async def create_table(cls):
        async with engine.begin() as connect:
            logger.info(f"Создаю базу данных {cls.__tablename__}...")
            await connect.run_sync(
                lambda sync_conn: cls.metadata.drop_all(sync_conn, tables=[cls.__table__])
            )
            await connect.run_sync(
                lambda sync_conn: cls.metadata.create_all(sync_conn, tables=[cls.__table__])
            )
            logger.info("База данных создана!")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Айди записи")
    course_id: Mapped[int] = mapped_column(nullable=False, comment="Айди курса")
    lesson_id: Mapped[int] = mapped_column(nullable=False, comment="Айди урока")
    user_id: Mapped[int] = mapped_column(primary_key=True, comment="Айди пользователя")
    course_name: Mapped[str] = mapped_column(nullable=False, comment='Название курса, к которому относится урок')
    lesson_title: Mapped[str] = mapped_column(nullable=False, comment='Название урока')
    status: Mapped[str] = mapped_column(default="in progress", comment="Статус выполнения урока")

    @classmethod
    async def create_table(cls):
        async with engine.begin() as connect:
            logger.info(f"Создаю базу данных {cls.__tablename__}...")
            await connect.run_sync(
                lambda sync_conn: cls.metadata.drop_all(sync_conn, tables=[cls.__table__])
            )
            await connect.run_sync(
                lambda sync_conn: cls.metadata.create_all(sync_conn, tables=[cls.__table__])
            )
            logger.info("База данных создана!")
