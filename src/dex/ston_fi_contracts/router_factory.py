from tonsdk.utils import Address

from src.config import config
from src.ton.tonapi_client_factory import TonapiClientFactory

from .router import Router


class RouterFactory:
    router: Router

    @staticmethod
    def init_router():
        RouterFactory.router = Router(
            address=Address(config.ston_fi.router_address),
            tonapi_client=TonapiClientFactory.get_tonapi_client(),
        )

    @staticmethod
    def get_router() -> Router:
        if RouterFactory.router is None:
            RouterFactory.init_router()

        return RouterFactory.router


RouterFactory.init_router()
