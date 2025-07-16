from datetime import datetime


class DateTime:
    @staticmethod
    def timestamp() -> int:
        return int(datetime.now().timestamp())

    @staticmethod
    def datetime() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def millisecond() -> int:
        return int(datetime.now().timestamp() * 1000)
