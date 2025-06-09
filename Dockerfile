FROM python:3.12-slim

# 安装 uv
RUN pip install --no-cache-dir uv -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install apache-skywalking -i https://mirrors.aliyun.com/pypi/simple/

# 设置工作目录并复制代码
WORKDIR /app
COPY . /app

RUN uv pip install . --system -i https://mirrors.aliyun.com/pypi/simple/

EXPOSE 8000

# 启动应用
CMD ["python", "main.py"]
