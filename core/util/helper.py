import json
import os
import traceback


class Helper:
    @staticmethod
    def get_root_path(markers=('pyproject.toml', '.git')):
        """
        查找项目根目录
        :param markers: 项目根目录的特征文件或文件夹
        :return: 项目根目录的绝对路径
        """
        path = os.path.abspath(os.path.dirname(__file__))
        while path != os.path.dirname(path):
            if any(os.path.exists(os.path.join(path, marker)) for marker in markers):
                return path
            path = os.path.dirname(path)
        return os.getcwd()

    @staticmethod
    def with_root_path(paths: list[str]) -> str:
        """
        拼接项目根目录
        """
        return str(os.path.join(Helper.get_root_path(), *paths))

    @staticmethod
    def exception_str(e: Exception, replace: bool) -> str:
        filtered = [
            line
            for line in traceback.format_tb(e.__traceback__)
            if 'site-packages/starlette' not in line and 'site-packages/fastapi' not in line
        ]
        tb_str = ''.join(filtered)
        tb_str += f'\n {str(e)}'
        if replace:
            return json.dumps({'error': tb_str}, ensure_ascii=False)
        return tb_str
