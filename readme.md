1. 生成uv环境
    ```shell
    uv venv
   .venv\Scripts\activate
   uv run uvicorn main:app
    ```

2. 安装包
    ```shell
    uv add pytest --dev
    ```

3. 启动
    ```shell
   测试环境: uvicorn main:app --reload
   测试环境: fastapi dev
   生产环境: fastapi run
   ```

4. 安装hook
   ```shell
     pre-commit install
   ```