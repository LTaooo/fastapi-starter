from datetime import datetime


class DateTime:
    @staticmethod
    def now() -> int:
        return int(datetime.now().timestamp())
