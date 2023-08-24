import json

from bilireq.auth import Auth

from ..store import cache_dir

gRPC_Auth: Auth = Auth()
bili_grpc_auth = cache_dir.joinpath("bili_grpc_auth.json")
bili_grpc_auth.touch(0o700, exist_ok=True)
data = json.loads(bili_grpc_auth.read_bytes())
gRPC_Auth.update(data)

# browser_cookies: Dict = {}
# browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie or "")
#
#
# def load_browser_cookies():
#     global browser_cookies
#     browser_cookies = json.loads(browser_cookies_file.read_bytes())
#
#
# def dump_browser_cookies():
#     browser_cookies_file.write_text(json.dumps(browser_cookies, ensure_ascii=False, indent=4))
