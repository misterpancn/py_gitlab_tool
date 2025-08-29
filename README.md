# GitLab提交查询工具

一个用于查询GitLab项目提交信息的Web应用程序。

## 功能特点

- 用户认证系统（JWT）
- 查询指定GitLab项目和分支在特定时间段内的提交信息
- 美观的用户界面，暖色调风格
- 完整的提交信息展示

## 技术栈

- 后端：FastAPI
- 前端：HTML, CSS, JavaScript
- 认证：JWT
- 模板引擎：Jinja2
- 包管理：uv

## 安装与运行

### 环境要求

- Python 3.10+
- uv包管理器

### 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv install
```

### 配置

在项目根目录创建`.env`文件，包含以下配置：

```
# 应用配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 登录凭证
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# GitLab配置
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_TOKEN=your_gitlab_token_here
```

### 运行应用

```bash
# 开发模式运行
python main.py
```

或者使用uvicorn直接运行：

```bash
uvicorn main:app --reload
```

应用将在 http://localhost:8000 上运行。

## 使用说明

1. 访问 http://localhost:8000/login 进入登录页面
2. 使用配置文件中设置的用户名和密码登录
3. 在操作页面输入GitLab项目ID、分支名和时间段
4. 点击查询按钮获取提交信息
5. 点击"查看详情"可查看完整的提交信息

## 项目结构

```
.
├── main.py                 # 主应用入口
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
├── src/                    # 源代码目录
│   ├── api/                # API路由
│   ├── auth/               # 认证相关
│   ├── models/             # 数据模型
│   ├── services/           # 服务层
│   ├── static/             # 静态资源
│   │   ├── css/            # CSS样式
│   │   └── js/             # JavaScript脚本
│   └── templates/          # HTML模板
└── .env                    # 环境变量配置
```
