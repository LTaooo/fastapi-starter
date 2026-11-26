# 构建阶段：按 uv.lock 同步依赖到 /app/.venv
FROM docker.m.daocloud.io/library/python:3.12-slim AS builder

RUN pip install --no-cache-dir uv -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev


# 运行阶段：只保留虚拟环境与源码，不安装 uv
FROM docker.m.daocloud.io/library/python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . /app

EXPOSE 8000

# 启动应用
CMD ["python", "main.py"]
