from sqlmodel import SQLModel


class BaseSQLModel(SQLModel):
    def get_primary_field(self) -> str:
        return 'id'

    def get_primary_key(self) -> str | None | int:
        return getattr(self, self.get_primary_field())
