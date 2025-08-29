"""
GitLab相关API
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.auth.auth import get_current_active_user
from src.models.gitlab import GitLabRequest, PaginatedCommits, TextExportFormat
from src.models.user import User
from src.services.gitlab_service import GitLabService

router = APIRouter()
gitlab_service = GitLabService()


@router.post("/commits", response_model=PaginatedCommits)
async def get_commits(
    request: GitLabRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    获取提交信息

    Args:
        request: GitLab请求参数
        current_user: 当前用户

    Returns:
        分页的提交信息
    """
    try:
        paginated_commits = gitlab_service.get_commits(
            request.project_id,
            request.branch,
            request.start_date,
            request.end_date,
            request.page,
            request.page_size,
            request.author_emails,
        )
        return paginated_commits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提交信息失败: {str(e)}")


@router.post("/commits/text", response_model=TextExportFormat)
async def get_commits_text(
    request: GitLabRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    获取文本格式的提交信息

    Args:
        request: GitLab请求参数
        current_user: 当前用户

    Returns:
        文本格式的提交信息
    """
    try:
        text_format = gitlab_service.get_commits_text_format(
            request.project_id,
            request.branch,
            request.start_date,
            request.end_date,
            request.author_emails,
        )
        return text_format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文本格式提交信息失败: {str(e)}")