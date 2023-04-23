<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="docs/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="docs/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-bilichat

_✨ 多功能的B站视频解析工具 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/djkcyl/nonebot-plugin-bilichat.svg" alt="license">
</a>

<a href="https://pypi.python.org/pypi/nonebot-plugin-bilichat">
  <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nonebot-plugin-bilichat">
</a>

<a href="https://pypi.python.org/pypi/nonebot-plugin-bilichat">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bilichat.svg" alt="pypi">
</a>

<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

<a href="https://pdm.fming.dev">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
</a>

<a href="https://onebot.dev/">
  <img src="https://img.shields.io/badge/OneBot-v11-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot">
</a>
<a href="https://onebot.dev/">
  <img src="https://img.shields.io/badge/OneBot-v12-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot">
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

![](docs/basic.png)
</details>

<details>
<summary>词云</summary>

![](docs/wordcloud.png)
</details>

<details>
<summary>视频总结</summary>

```markdown
## 总结
高通第二代骁龙7+的工程机，拥有台积电4nm工艺，CPU规格和骁龙8+一模一样，GPU规格上是新的Adreno 700架构，性能表现出众，能效曲线稍逊于8+，但中低频段能效水平相同，终端机价格如果能做到1500-2000元，竞争力还是很足的。 

## 要点
- 💻 第二代骁龙7+拥有台积电4nm工艺和与骁龙8+一样的CPU规格。
- 🎮 新的Adreno 700架构GPU规格性能强，比上一代7Gen1强了超过一倍。
- 📈 能效曲线稍逊于8+，但中低频段能效水平相同。
- 💰 如果终端机价格做到1500-2000元，竞争力还是很足的。
- 🧪 高通自己也意识到骁龙7系列的竞争力问题，这也使其成了必须要解决的一个问题。
- 🕹️ 7+ Gen2就是8+的CPU，旗舰规格下放，最大的受益者是大型游戏。
```

</details>

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-bilichat

注: 由于 nb-cli 不支持依赖组，因此需要启用词云和AI总结的用户要通过其他的包管理器安装额外的依赖

    pip install nonebot-plugin-bilichat[all]

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-bilichat[all]
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-bilichat[all]
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-bilichat[all]
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-bilichat[all]
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_bilichat"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置, 配置均为**非必须项**

### 通用配置项

| 配置项 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| bilichat_block              | bool      | False | 是否拦截事件(防止其他插件二次解析) |
| bilichat_enable_private     | bool      | True  | 是否允许响应私聊 |
| bilichat_enable_self        | bool      | False | 是否允许响应自身的消息 |
| bilichat_enable_v12_channel | bool      | True  | ~~是否允许响应频道消息(ob12专属)~~(暂未实现) |
| bilichat_enable_unkown_src  | bool      | False | 是否允许响应未知来源的消息 |
| bilichat_whitelist          | list[str] | []    | **响应**的群聊(频道)名单, 会覆盖黑名单 |
| bilichat_blacklist          | list[str] | []    | **不响应**的群聊(频道)名单 |
| bilichat_dynamic_font       | str       | None  | 视频信息及词云图片使用的字体 |
| bilichat_cd_time            | int       | 120   | 对同一视频的响应冷却时间(防止刷屏) |
| bilichat_neterror_retry     | int       | 3     | 对部分网络请求错误的尝试次数 |
| bilichat_use_bcut_asr       | bool      | True  | 是否在**没有字幕时**调用必剪接口生成字幕 |

注:

1. 由于 OneBot 协议未规定是否应上报自身事件，因此在不同的场景下能否获取自身事件并不一定，`bilichat_enable_self` 实际能否生效也与之相关
2. 当 `bilichat_whitelist` 存在时，`bilichat_blacklist` 将会被禁用
3. `bilichat_dynamic_font` 可填写自定义的字体url，但并不推荐修改
4. 当使用 `bcut_asr` 接口来生成AI字幕时，根据视频时长和网络情况有可能会识别失败，Bot会提示 `BCut-ASR conversion failed due to network error`。可以通过调高 `bilichat_neterror_retry` 次数或几分钟后重试来尝试重新生成字幕

### 基础信息配置项

| 配置项 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| bilichat_basic_info          | bool | True | 是否开启视频基本信息 |
| bilichat_reply_to_basic_info | bool | True | 后续消息是否回复基础信息(关闭则回复发送者的信息) |

### 词云配置项

开启此功能需要安装对应的依赖 `nonebot-plugin-bilichat[wordcloud]`

| 配置项 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| bilichat_word_cloud  | bool | True | 是否开启词云功能 |

注：词云功能在 python3.11 中由于 `wordcloud` 包安装失败暂时无法启用，请不要在 3.11 中开启此功能

### AI视频总结配置项

开启此功能需要安装对应的依赖 `nonebot-plugin-bilichat[openai,newbing]`

| 配置项 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| bilichat_newbing_cookie      | str       | None               | newbing的cookie文件路径(获取方式参考[这里](https://github.com/acheong08/EdgeGPT#getting-authentication-required)和[这里](https://github.com/Harry-Jing/nonebot-plugin-bing-chat#%EF%B8%8F-%E9%85%8D%E7%BD%AE)) , 若留空则禁用newbing总结 |
| bilichat_newbing_token_limit | int       | 0                  | newbing请求的文本量上限, 0为无上限 |
| bilichat_newbing_preprocess  | bool      | True               | 是否对newbing的返回值进行预处理, 以去除其中不想要的内容 |
| bilichat_openai_token        | str       | None               | openai的apikey, 若留空则禁用openai总结 |
| bilichat_openai_proxy        | str       | None               | 访问openai或newbing使用的代理地址 |
| bilichat_openai_model        | str       | gpt-3.5-turbo-0301 | 使用的语言模型名称 |
| bilichat_openai_token_limit  | int       | 3500               | 请求的文本量上限, 计算方式可参考[tiktoken](https://github.com/openai/tiktoken) |

注:

1. openai 与 newbing 目前均需求科学上网才能使用，国内服务器请务必填写 `bilichat_openai_proxy` 或全局透明代理
2. 如果同时填写了 `bilichat_openai_token` 和 `bilichat_newbing_cookie`，则会使用 `newbing` 进行总结, 并在 `newbing` 总结失败时使用 `openai` 进行总结
3. `newbing` 和 `openai` 均有缓存机制，同一视频在**获取到正常的总结内容后**不会重复发送请求，如需刷新请求内容可以手动删除对应视频的缓存文件或整个缓存文件夹
4. 经测试，目前 `newbing` 至少能总结 12000 字符以上的文本，推测 token 上限应为 `gpt-4-32k-0314` 的 `32200` token，但过长的内容易造成输出内容包含额外内容或总结失败，因此也建议设置一个合理的 token 上限 ~~（反正不要钱，要啥自行车）~~
5. 由于 `newbing` 限制较大，也不如 `openai` 听话，且需要联网查询资料，因此使用体验并不如 chatgpt ~~（反正不要钱，要啥自行车）~~

## 🎉 使用

直接发送视频(专栏)链接即可

### 参数表

在发送视频时，可以额外添加以下类似 shell 指令的参数，进而对解析流程进行调整。例如

```shell
BV12v4y1E7NT --refresh
BV12v4y1E7NT -r # 可以使用简写
BV12v4y1E7NT -r --no-cache # 可以多个参数混用
-r BV12v4y1E7NT -n # 虽然不建议，但确实可以把参数放前面
```

| 指令 | 简写 | 说明 |
|:-----:|:----:|:----:|
| --no-cache | -n | 本次总结禁用缓存(不会影响已存在的缓存文件) |
| --refresh  | -r | 刷新此视频的词云和总结缓存(会覆盖已存在的缓存文件) |

### 指令表

> 正在开发指令相关，请无视这里的模板
> 指令设计方案征集中，如果有什么想要实现的功能可以在issue中提出

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 指令1 | 主人 | 否 | 私聊 | 指令说明 |
| 指令2 | 群员 | 是 | 群聊 | 指令说明 |

## 🙏 感谢

在此感谢以下开发者(项目)对本项目做出的贡献：

- [BibiGPT](https://github.com/JimmyLv/BibiGPT) 项目灵感来源
- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 易姐收集的各种 BiliBili Api 及其提供的 gRPC Api 调用方案
- [BBot-Graia](https://github.com/djkcyl/BBot-Graia) 功能来源 ~~(我 牛 我 自 己)~~
- [ABot-Graia](https://github.com/djkcyl/ABot-Graia) 永远怀念最好的 ABot 🙏
- [nonebot-plugin-template](https://github.com/A-kirami/nonebot-plugin-template): 项目的 README 模板

## ⏳ Star 趋势

[![Stargazers over time](https://starchart.cc/djkcyl/nonebot-plugin-bilichat.svg)](https://starchart.cc/djkcyl/nonebot-plugin-bilichat)
