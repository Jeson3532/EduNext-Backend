from pydantic_settings import BaseSettings, SettingsConfigDict
from .__init__ import env_path


class DBConfig(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: str
    DBNAME: str

    model_config = SettingsConfigDict(env_file=env_path, extra="allow")
