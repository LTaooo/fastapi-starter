from core.di.container import Container


class ARepository:
    pass


class AService:
    def __init__(self, a_repository: ARepository) -> None:
        self.a_repository = a_repository


class AController:
    def __init__(self, a_service: AService) -> None:
        self.a_service = a_service


def test_container():
    container = Container()
    container.set(ARepository, ARepository())
    container.set(AService, AService(container.get(ARepository)))
    container.set(AController, AController(container.get(AService)))
    a_controller = container.get(AController)
    assert isinstance(a_controller, AController)


def test_auto_resolve():
    container = Container()
    a_controller = container.get(AController)
    assert isinstance(a_controller, AController)
    b_controller = container.get(AController)
    assert a_controller is b_controller
