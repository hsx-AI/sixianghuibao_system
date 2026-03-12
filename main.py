from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import auth as auth_routes
from app.routes import feedback as feedback_routes
from app.routes import integration as integration_routes
from app.routes import reports as report_routes
from app.routes import users as user_routes
from app.utils.backup import backup_database


def create_app() -> FastAPI:
    app = FastAPI(title="Thought Report Review System")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],  # 允许前端读取文件名
    )

    # 添加 /api 前缀
    app.include_router(auth_routes.router, prefix="/api")
    app.include_router(feedback_routes.router, prefix="/api")
    app.include_router(integration_routes.router, prefix="/api")
    app.include_router(report_routes.router, prefix="/api")
    app.include_router(user_routes.router, prefix="/api")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        # 启动时检查并执行数据库备份
        backup_database()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8173, reload=True)
