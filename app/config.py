from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    app_name: str = "Thought Report Review"
    secret_key: str = "change_me_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    database_url: str = f"sqlite:///{(base_dir / 'data' / 'app.db').as_posix()}"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
