1. 生成conda环境
    ```shell
    conda env create -f environment.yml
    ```

2. 安装包
    ```shell
    conda install -c conda-forge aiomysql 
    ```

3. 更新依赖
    ```shell
    conda env export   --no-builds  > environment.yml
    ```
4. 启动
    ```shell
   uvicorn main:app --reload
   ```