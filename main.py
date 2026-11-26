from core.dto.common_res import CommonRes
from core.exception.handle import exception_handle
from core.middleware import middleware
from routes import routes
from fastapi import FastAPI
from config.app_config import AppConfig
from core.config import Config
from core.lifespan import lifespan
from core.openapi import openapi
from core import documentation
import uvicorn

app_config = Config.get(AppConfig)
app = FastAPI(
    lifespan=lifespan,
    title=app_config.app_name,
    debug=app_config.app_debug,
    responses={200: CommonRes(data=None).model_dump()},
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    root_path=app_config.app_root_path,
)
exception_handle.register(app)
app.openapi = openapi(app.openapi)
documentation.register(app, app_config)
routes.register(app)
middleware.register(app)

if __name__ == '__main__':
    config = Config.get(AppConfig)
    uvicorn.run(
        'main:app',
        host=config.app_host,
        port=config.app_port,
        workers=config.app_workers,
        log_config=None,
    )
