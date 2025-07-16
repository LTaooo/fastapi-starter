from core.util.datetime import DateTime


class AutoTime:
    def _get_update_time_field(self) -> str:
        return 'updated_at'

    def _get_create_time_field(self) -> str:
        return 'created_at'

    def _get_now_time(self) -> str | int:
        return DateTime.timestamp()

    def auto_set_time(self):
        now_time = self._get_now_time()
        if getattr(self, self._get_create_time_field(), None) is None:
            setattr(self, self._get_create_time_field(), now_time)
        setattr(self, self._get_update_time_field(), now_time)
