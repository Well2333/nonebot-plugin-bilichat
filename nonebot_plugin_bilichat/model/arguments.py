from nonebot.rule import ArgumentParser, Namespace

parser = ArgumentParser()
parser.add_argument("--no-cache", "-n", action="store_true", help="disable caching this time")
parser.add_argument("--refresh", "-r", action="store_true", help="refresh cache file")


class Options(Namespace):
    no_cache: bool = False
    refresh: bool = False
