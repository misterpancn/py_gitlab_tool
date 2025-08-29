"""
GitLab服务
"""
import os
import math
from datetime import date
from typing import List, Optional
import requests
from dotenv import load_dotenv

from src.models.gitlab import Commit, PaginatedCommits, TextExportFormat

# 加载环境变量
load_dotenv()

# GitLab配置
GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")


class GitLabService:
    """GitLab服务类"""

    def __init__(self):
        """初始化"""
        self.api_url = GITLAB_API_URL
        self.token = GITLAB_TOKEN
        self.headers = {"PRIVATE-TOKEN": self.token} if self.token else {}

    def _is_merge_commit(self, commit_title: str, commit_message: str) -> bool:
        """
        判断是否为合并提交

        Args:
            commit_title: 提交标题
            commit_message: 提交信息

        Returns:
            是否为合并提交
        """
        # 检查标题或消息中是否包含"Merge branch"字样
        merge_indicators = ["Merge branch", "Merge remote-tracking branch", "Merge pull request"]
        for indicator in merge_indicators:
            if indicator in commit_title or indicator in commit_message:
                return True
        return False

    def _filter_by_author_emails(self, commits: List[Commit], author_emails: Optional[str]) -> List[Commit]:
        """
        按作者邮箱筛选提交记录

        Args:
            commits: 提交记录列表
            author_emails: 作者邮箱，多个邮箱用逗号分隔

        Returns:
            筛选后的提交记录列表
        """
        if not author_emails:
            return commits
        
        # 将邮箱字符串分割为列表，并去除空白
        email_list = [email.strip().lower() for email in author_emails.split(',') if email.strip()]
        
        # 如果没有有效的邮箱，返回所有提交
        if not email_list:
            return commits
        
        # 筛选匹配邮箱的提交
        filtered_commits = [
            commit for commit in commits 
            if commit.author_email.lower() in email_list
        ]
        
        return filtered_commits

    def get_all_commits(
        self, project_id: str, branch: str, start_date: date, end_date: date,
        author_emails: Optional[str] = None
    ) -> list[Commit]:
        """
        获取所有提交信息（不分页）

        Args:
            project_id: 项目ID
            branch: 分支名
            start_date: 开始日期
            end_date: 结束日期
            author_emails: 作者邮箱，多个邮箱用逗号分隔

        Returns:
            提交信息列表
        """
        url = f"{self.api_url}/projects/{project_id}/repository/commits"
        
        # 格式化日期为ISO 8601格式
        since = start_date.isoformat()
        until = end_date.isoformat()
        
        params = {
            "ref": branch,  # 使用ref参数指定分支，而不是ref_name
            "since": f"{since}T00:00:00Z",
            "until": f"{until}T23:59:59Z",
            "all": "false",  # 设置为false，只获取指定分支的提交
            "per_page": 100,  # 每页获取的提交数量
        }
        
        commits = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                # 如果请求失败，返回空列表
                return []
            
            page_commits = response.json()
            if not page_commits:
                # 如果没有更多提交，跳出循环
                break
            
            # 将API返回的提交信息转换为Commit模型，并过滤掉合并提交
            for commit_data in page_commits:
                # 检查是否为合并提交
                if not self._is_merge_commit(commit_data["title"], commit_data["message"]):
                    commit = Commit(
                        id=commit_data["id"],
                        short_id=commit_data["short_id"],
                        title=commit_data["title"],
                        author_name=commit_data["author_name"],
                        author_email=commit_data["author_email"],
                        created_at=commit_data["created_at"],
                        message=commit_data["message"],
                    )
                    commits.append(commit)
            
            # 检查是否有下一页
            if len(page_commits) < params["per_page"]:
                break
            
            page += 1
        
        # 按作者邮箱筛选
        if author_emails:
            commits = self._filter_by_author_emails(commits, author_emails)
            
        return commits

    def get_commits(
        self, project_id: str, branch: str, start_date: date, end_date: date, 
        page: int = 1, page_size: int = 10, author_emails: Optional[str] = None
    ) -> PaginatedCommits:
        """
        获取分页的提交信息

        Args:
            project_id: 项目ID
            branch: 分支名
            start_date: 开始日期
            end_date: 结束日期
            page: 页码，从1开始
            page_size: 每页数量
            author_emails: 作者邮箱，多个邮箱用逗号分隔

        Returns:
            分页提交信息
        """
        # 先获取所有提交记录
        all_commits = self.get_all_commits(project_id, branch, start_date, end_date, author_emails)
        
        # 计算总数和总页数
        total = len(all_commits)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        # 安全检查页码
        if page > total_pages:
            page = total_pages
        
        # 计算当前页的数据
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total)
        current_page_commits = all_commits[start_idx:end_idx]
        
        # 构建分页结果
        paginated_result = PaginatedCommits(
            items=current_page_commits,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        return paginated_result

    def get_commits_text_format(
        self, project_id: str, branch: str, start_date: date, end_date: date,
        author_emails: Optional[str] = None
    ) -> TextExportFormat:
        """
        获取文本格式的提交信息

        Args:
            project_id: 项目ID
            branch: 分支名
            start_date: 开始日期
            end_date: 结束日期
            author_emails: 作者邮箱，多个邮箱用逗号分隔

        Returns:
            文本格式的提交信息
        """
        # 获取所有提交记录
        commits = self.get_all_commits(project_id, branch, start_date, end_date, author_emails)
        
        # 生成文本格式
        text_lines = []
        for i, commit in enumerate(commits, 1):
            text_lines.append(f"{i}、{commit.author_name}：{commit.title}")
        
        # 使用换行符连接所有行
        text_content = "\n".join(text_lines)
        
        return TextExportFormat(content=text_content)