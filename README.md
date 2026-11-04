# fastapi-starter

## 环境要求

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

```shell
# 安装 uv 后安装 Python 3.12
uv python install 3.12
```

## 安装依赖

```shell
uv sync
```

## 配置

复制 `.env.example` 为 `.env` 并按需修改。`APP_ENV` 决定额外加载哪个环境配置文件：

| APP_ENV | 加载文件 |
| --- | --- |
| `dev`（默认） | `.env`，存在 `.env.dev` 时合并 |
| `test` | `.env` + `.env.test` |
| `prod` | `.env` + `.env.prod` |

同名配置以 `.env.<APP_ENV>` 为准，未覆盖项来自 `.env`；系统环境变量优先级最高。`APP_ENV` 本身需要配置在系统环境变量或 `.env` 中。`.env` 与 `.env.<APP_ENV>` 均已被 git 忽略。

MySQL、Redis、RabbitMQ、MCP、Nacos、飞书告警均可通过 `enable` 关闭（Nacos 使用 `NACOS_ENABLE`）。关闭后不会建立连接：

```dotenv
mysql.enable=true
redis.enable=true
rabbitmq.enable=false
mcp.enable=false
NACOS_ENABLE=false
feishu.enable=false
```

## 启动

开发环境：

```shell
uv run uvicorn main:app --reload
```

或按 `workers` 配置启动多进程：

```shell
uv run python main.py
```

## 代码检查

```shell
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## 测试

测试为集成测试，需要可用的 MySQL。先在 `.env` 中配置 `mysql.*`，并提前创建数据库与 `book` 表：

```shell
uv run pytest
```

## Docker

```shell
docker build -t fastapi-starter .
docker run --rm -p 8000:8000 --env-file .env fastapi-starter
```

镜像以非 root 用户运行，`.env`、`.git`、`.venv` 等文件通过 `.dockerignore` 排除。若需要 `.env.<APP_ENV>`，挂载到容器内对应路径并设置 `APP_ENV`。

## pre-commit

```shell
pre-commit install
```
