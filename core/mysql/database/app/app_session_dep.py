from typing import Annotated

from fastapi import Depends

from core.mysql.database.app.app_database import AppDatabase
from core.mysql.database.app.app_session import AppSession

SessionDep = Annotated[AppSession, Depends(AppDatabase.get_session)]
