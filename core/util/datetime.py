from datetime import datetime


class DateTime:
    @staticmethod
    def now() -> int:
        return int(datetime.now().timestamp())

    @staticmethod
    def datetime() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
