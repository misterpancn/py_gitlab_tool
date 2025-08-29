"""
用户模型
"""
from pydantic import BaseModel


class User(BaseModel):
    """用户模型"""
    username: str


class UserInDB(User):
    """数据库中的用户模型"""
    hashed_password: str


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: str | None = None
