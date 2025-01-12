<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="docs/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="docs/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-bilichat

_✨ 多功能的 B 站视频解析工具 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/djkcyl/nonebot-plugin-bilichat.svg" alt="license">
</a>

<a href="https://pypi.python.org/pypi/nonebot-plugin-bilichat">
  <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nonebot-plugin-bilichat">
</a>

<a href="https://pypi.python.org/pypi/nonebot-plugin-bilichat">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bilichat.svg" alt="pypi">
</a>

<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

<a href="https://pdm.fming.dev">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
</a>

<a href="https://jq.qq.com/?_wv=1027&k=5OFifDh">
  <img src="https://img.shields.io/badge/QQ%E7%BE%A4-768887710-orange?style=flat-square" alt="QQ Chat Group">
</a>
<a href="https://jq.qq.com/?_wv=1027&k=7LWx6q4J">
  <img src="https://img.shields.io/badge/QQ%E7%BE%A4-720053992-orange?style=flat-square" alt="QQ Chat Group">
</a>

</div>

## 📖 介绍

视频链接解析，并根据其内容生成**基本信息**、**词云**和**内容总结**

<details>
<summary>手机端视图</summary>

![](docs/mobile.png)

</details>

<details>
<summary>基本信息</summary>

![style_blue](docs/style_blue.png)

</details>


## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-bilichat

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-bilichat

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-bilichat

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-bilichat

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-bilichat

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_bilichat"]

</details>

## ⚙️ 配置

由于本项目存在大量支持热重载的配置参数，因此不能使用 `nonebot2` 的默认配置文件 `.env`，而是使用一个单独的 `config.yaml` 文件来存储配置。您可以通过在 `.env` 文件中设置 `bilichat_config_path` 来手动指定该文件的位置。

### 配置文件示例

您可以参考 [配置文件模板](https://github.com/Well2333/nonebot-plugin-bilichat/blob/v6.0.5/nonebot_plugin_bilichat/static/config.yaml) 来了解配置项及其含义。

## 🔌 API

> 从 6.0.0 版本开始，`bilibili` 请求已迁移至 [bilichat-request](https://github.com/Well2333/bilichat-request) 模块，并改为 API 通讯方式。这一改进带来了多项优化：支持一对多的负载均衡、提升 Cookies 管理效率，并有效应对更严格的风控措施。同时，原本需要浏览器操作（如截图）的任务被移至远程服务器处理，从而减轻本地机器的内存压力。

### 部署远程 API

在部署完 [bilichat-request](https://github.com/Well2333/bilichat-request) 后，您只需在配置文件中填写相应的 API 地址即可。

```yaml
api:
  request_api:
    - api: "https://api.example.com"  # API 地址
      token: "your_api_token"         # API Token (如果服务端未设置，留空)
      weight: 1                       # 权重，用于负载均衡，数值越大优先级越高
      enable: true                    # 是否启用该 API
    - api: "https://api2.example.com" # 可配置多个 API 地址
      token: ...
      weight: ...
      enable: false
```

### 集成式部署 API

若您需要在 `nonebot2` 中集成 [bilichat-request](https://github.com/Well2333/bilichat-request)，请确保已经安装并加载了 [FastAPI Driver](https://nonebot.dev/docs/next/advanced/driver#fastapi%E9%BB%98%E8%AE%A4)，并执行以下命令安装依赖：

```bash
pip install bilichat-request
```

在配置文件中开启本地 API 服务：

```yaml
api:
  local_api_config:  # 本地 API 配置
    enable: false    # 是否启用本地 API（将其改为 true 开启本地 API）
    api_access_token: ""  # 本地 API Token
    api_path: bilichatapi  # 本地 API 挂载路径
    api_sub_dynamic_limit: 720/hour  # 动态订阅限速
    api_sub_live_limit: 1800/hour    # 直播订阅限速
    # 更多配置请参考 bilichat-request 的配置文件
```

上述配置会作为启动参数传递给 `bilichat-request`。其他额外配置项可参考 [bilichat-request 配置文件](https://github.com/Well2333/bilichat-request/blob/main/src/bilichat_request/config.py)。

### 注意事项

- 初次启动时，系统将自动下载 Playwright 的浏览器内核。确保网络畅通。如果下载失败，您可以尝试设置 `playwright_download_host` 为国内镜像地址。

## 🎉 使用

直接发送视频(专栏)链接即可

### 参数表

在发送视频时，可以额外添加以下类似 shell 指令的参数，进而对解析流程进行调整。例如

```shell
BV12v4y1E7NT --force
BV12v4y1E7NT -f # 可以使用简写
```

|  指令   | 简写  |            说明            |
| :-----: | :---: | :------------------------: |
| --force |  -f   | 忽略 cd 时间，强制解析视频 |

### 指令表

指令部分由 `指令前缀` 和 `指令名` 组成，其中 `指令前缀` 包含 `COMMAND_START` `bilichat_cmd_start` `COMMAND_SEP` 三部分，默认的 `指令前缀` 为 `/bilichat.` ，即完整的指令为 `/bilichat.xxx`

`指令前缀` 部分也是可以修改的，例如 .env 中填入如下设置即可实现无 `指令前缀`

```dotenv
COMMAND_SEP=[""]
COMMAND_START=[""]
bilichat_cmd_start=""
```

`指令名` 如下表所示，其中除登录相关的指令均可自定义，可参考上文的 [指令及订阅配置项](#指令及订阅配置项)

|     指令     |  权限  |  范围  |            参数             |                说明                |
| :----------: | :----: | :----: | :-------------------------: | :--------------------------------: |
|     sub      |  主人  |  群聊  |      UP 主的昵称或 UID      |              添加订阅              |
|    unsub     |  主人  |  群聊  | UP 主的昵称或 UID，或 `all` |      移除订阅，all 时为全移除      |
|    check     | 无限制 |  群聊  |  UP 主的昵称或 UID，或留空  | 查看本群订阅列表或指定 UP 主的配置 |
| checkdynamic | 无限制 | 无限制 |      UP 主的昵称或 UID      |    查看指定 UP 主的最新一条动态    |
|  checklogin  |  主人  | 无限制 |             无              |      查看当前已登录的全部账号      |
|   qrlogin    |  主人  | 无限制 |             无              |   使用二维码登录 B 站，防止风控    |
|    logout    |  主人  | 无限制 |         账号的 UID          |           登出指定的账号           |

## 🙏 感谢

在此感谢以下开发者(项目)对本项目做出的贡献：

-   [BibiGPT](https://github.com/JimmyLv/BibiGPT) 项目灵感来源
-   [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 易姐收集的各种 BiliBili Api 及其提供的 gRPC Api 调用方案
-   [HarukaBot](https://github.com/SK-415/HarukaBot) 功能来源
-   [BBot-Graia](https://github.com/djkcyl/BBot-Graia) 功能来源 ~~(我 牛 我 自 己)~~
-   [ABot-Graia](https://github.com/djkcyl/ABot-Graia) 永远怀念最好的 ABot 🙏
-   [bilireq](https://github.com/SK-415/bilireq) 项目曾经使用的 bilibili 请求库
-   [nonebot-plugin-template](https://github.com/A-kirami/nonebot-plugin-template): 项目的 README 模板
-   [Misaka-Mikoto-Tech](https://github.com/Misaka-Mikoto-Tech) 为本项目提交了多项 BUG 修复和代码参考
-   [hamo-reid](https://github.com/hamo-reid) 为 style_blue 绘制了界面
-   [dynamicrender](https://pypi.org/project/dynrender-skia/) 曾经提供了 t2i 和动态渲染
-   [ALC](https://github.com/nonebot/plugin-alconna) 提供跨平台支持
-   [凛雅](https://github.com/linya64/bili) 提供 QQ 免费 bili 推送姬 成品 BOT 服务

## ⏳ Star 趋势

[![Stargazers over time](https://starchart.cc/Well2333/nonebot-plugin-bilichat.svg)](https://starchart.cc/Well2333/nonebot-plugin-bilichat)
