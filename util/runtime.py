from core.context import Context


class Runtime:
    @classmethod
    def get_env(cls) -> str:
        return Context.get_envs().get("APP_ENV", "dev")
