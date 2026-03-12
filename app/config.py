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

    # 与主系统 OA 约定的 SSO 签名密钥（用于校验 ticket，需与主系统 SSO_SECRET 一致）
    sso_secret: str = "18400021209"
    # 前端站点根 URL（用于 SSO 登录后重定向，如 http://localhost:5173 或留空表示同源）
    frontend_base_url: str = "http://10.42.60.223:5173"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
