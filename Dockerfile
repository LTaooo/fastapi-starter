FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装 uv
RUN pip install --no-cache-dir uv -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN useradd --create-home --uid 10001 appuser

# 设置工作目录并复制依赖清单
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

# 复制代码
COPY --chown=appuser:appuser . /app
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# 启动应用
CMD [".venv/bin/python", "main.py"]
