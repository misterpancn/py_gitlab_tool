"""
GitLab相关模型
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class GitLabRequest(BaseModel):
    """GitLab请求模型"""
    project_id: str
    branch: str
    start_date: date
    end_date: date
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量，默认10，最大100")
    author_emails: Optional[str] = Field(default=None, description="作者邮箱，多个邮箱用逗号分隔")


class Commit(BaseModel):
    """提交信息模型"""
    id: str
    short_id: str
    title: str
    author_name: str
    author_email: str
    created_at: str
    message: str


class PaginatedCommits(BaseModel):
    """分页提交信息模型"""
    items: List[Commit]
    total: int
    page: int
    page_size: int
    total_pages: int


class TextExportFormat(BaseModel):
    """文本导出格式"""
    content: str