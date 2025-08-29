"""
主应用程序入口
"""
import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Annotated
from dotenv import load_dotenv

from src.api import auth as auth_router
from src.api import gitlab as gitlab_router
from src.auth.auth import get_current_active_user
from src.models.user import User

load_dotenv()

HTTP_HOST = os.getenv("HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.getenv("HTTP_PORT", 8080))
# 创建FastAPI应用
app = FastAPI(title="GitLab提交查询工具")

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default_secret_key"))

# 挂载静态文件
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="src/templates")

# 注册API路由
app.include_router(auth_router.router, prefix="/api", tags=["认证"])
app.include_router(gitlab_router.router, prefix="/api", tags=["GitLab"])


# 自定义异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常"""
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # 对于401认证错误，返回特殊的响应
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": "认证失败，请重新登录",
                "redirect": "/login",
                "auth_error": True
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
async def logout(request: Request):
    """登出"""
    response = RedirectResponse(url="/login")
    request.session.pop("user", None)
    return response


@app.get("/api/check-auth")
async def check_auth(current_user: Annotated[User, Depends(get_current_active_user)]):
    """检查认证状态"""
    return {"authenticated": True, "username": current_user.username}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HTTP_HOST, port=HTTP_PORT, reload=True)