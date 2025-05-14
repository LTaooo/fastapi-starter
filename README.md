1. 安装UV
    ```shell
    存在系统Python:
    pip install uv
   
    不存在系统Python 
    先安装uv: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    再通过uv安装python: uv python install 3.12
      
    参考: https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1
    ```
2. 生成uv环境
    ```shell
    uv sync
    uv run uvicorn main:app
    ```

3. 安装包
    ```shell
    uv add pytest --dev
    ```

4. 启动
    ```shell
   测试环境: uvicorn src.main:app --reload
   测试环境: fastapi dev
   生产环境: fastapi run
   ```

5. 同步包
    ```shell
    uv sync
    ```

6. 安装hook
   ```shell
     pre-commit install
   ```