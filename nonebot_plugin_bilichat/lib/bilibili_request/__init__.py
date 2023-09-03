import httpx

from .gRPC import grpc_get_playview, grpc_get_view_info  # noqa: F401
from .restAPI import (  # noqa: F401
    get_b23_url,
    get_dynamic,
    get_player,
    get_user_dynamics,
    get_user_space_info,
    search_user,
)

hc = httpx.AsyncClient(
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39"
        )
    },
    follow_redirects=True,
)
