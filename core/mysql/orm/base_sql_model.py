from sqlalchemy.orm import DeclarativeBase


class BaseSQLModel(DeclarativeBase):
    def get_primary_field(self) -> str:
        return 'id'

    def get_primary_key(self) -> str | None | int:
        return getattr(self, self.get_primary_field())
