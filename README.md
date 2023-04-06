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
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bilichat.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

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

## 📝 TODO

- [x] 简易的黑(白)名单系统
- [ ] 更好的权限控制系统
- [ ] 图片形式发送视频总结

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

在 nonebot2 项目的`.env`文件中添加下表中的配置, 配置均为**非必须项**

| 配置项 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| bilichat_block              | bool      | False              | 是否拦截事件(防止其他插件二次解析) |
| bilichat_enable_private     | bool      | True               | 是否允许响应私聊 |
| bilichat_enable_v12_channel | bool      | True               | 是否允许响应频道消息(ob12专属) |
| bilichat_enable_unkown_src  | bool      | False              | 是否允许响应未知来源的消息 |
| bilichat_whitelist          | list[str] | []                 | **响应**的群聊(频道)名单, 会覆盖黑名单 |
| bilichat_blacklist          | list[str] | []                 | **不响应**的群聊(频道)名单 |
| bilichat_dynamic_font       | str       | None               | 视频信息及词云图片使用的字体 |
| bilichat_cd_time            | int       | 120                | 对同一视频的响应冷却时间(防止刷屏) |
| bilichat_use_bcut_asr       | bool      | True               | 是否在**没有字幕时**调用必剪接口生成字幕 |
| bilichat_word_cloud         | bool      | True               | 是否开启词云功能 |
| bilichat_openai_token       | str       | None               | openai的apikey, 若留空则禁用AI总结 |
| bilichat_openai_proxy       | str       | None               | 访问openai使用的代理地址 |
| bilichat_openai_model       | str       | gpt-3.5-turbo-0301 | 使用的语言模型名称 |
| bilichat_openai_token_limit | int       | 3500               | 请求的文本量上限, 计算方式可参考[tiktoken](https://github.com/openai/tiktoken) |

## 🎉 使用

直接发送视频(专栏)链接即可

### 指令表

> 正在开发指令相关，请无视这里的模板

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
