from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from routers import users
from routers import auth

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "13579013579Ahn!",
    "database": "ablymacro"
}

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Hanacoin API",
        version="1.0.0",
        description="Custom login via /token",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2Password": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token",  # 위에서 정의한 경로
                    "scopes": {}
                }
            }
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"OAuth2Password": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(users.router)
app.include_router(auth.router)