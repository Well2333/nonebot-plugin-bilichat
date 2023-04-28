import re
from typing import Any, Dict, List, Literal

from nonebot.log import logger
from pydantic import BaseModel, validator
from typing_extensions import Literal

from .exception import (
    BingChatAccountReachLimitException,
    BingChatInvalidSessionException,
    BingChatResponseException,
    BingChatUnknownException,
)


class BingChatResponse(BaseModel):
    raw: Dict[Any, Any]

    @validator("raw")
    def raw_validator(cls, v: Dict[Any, Any]) -> Dict[Any, Any]:
        logger.debug(v)
        if v.get("item", {}).get("result", {}).get("value") == "Throttled":
            logger.error("<Bing账号到达今日请求上限>")
            raise BingChatAccountReachLimitException("<Bing账号到达今日请求上限>")

        if v.get("item", {}).get("result", {}).get("value") == "InvalidSession":
            logger.error("<无效的会话>")
            raise BingChatInvalidSessionException("<无效的会话>")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("offense", "None") != "None"
        ):
            logger.error("<Bing检测到冒犯性文字，拒绝回答")
            raise BingChatResponseException("<Bing检测到冒犯性文字，拒绝回答>")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("hiddenText", "")
        ):
            hidden_text = v.get("item", {}).get("messages", [])[1].get("hiddenText")
            logger.error(f"<Bing检测到敏感问题，自动隐藏>\n{hidden_text}")
            raise BingChatResponseException(f"<Bing检测到敏感问题，自动隐藏>\n{hidden_text}")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("text", "")
        ):
            return v

        logger.error("<未知的错误>")
        raise BingChatUnknownException("<未知的错误, 请管理员查看控制台>")

    @staticmethod
    def remove_quote_str(string: str) -> str:
        return re.sub(r"\[\^\d+?\^]", "", string)

    @property
    def content_answer(self):
        return self.remove_quote_str(self.raw["item"]["messages"][1]["text"])

    @property
    def content_reference(self):
        return "\n".join(f"- {i}" for i in self.source_attributions_url_list)

    @property
    def content_suggested_question(self):
        print(self.suggested_question_list)
        return "\n".join(f"- {i}" for i in self.suggested_question_list)

    def adaptive_cards(self) -> List[str]:
        return list(self.raw["item"]["messages"][1]["adaptiveCards"][0]["body"])

    @property
    def source_attributions_url_list(self):
        return [i["seeMoreUrl"] for i in self.raw["item"]["messages"][1]["sourceAttributions"]]

    @property
    def suggested_question_list(self):
        return [i["text"] for i in self.raw["item"]["messages"][1]["suggestedResponses"]]

    def get_content(self, type: Literal["answer", "reference", "suggested-question"] = "answer"):
        if type == "answer":
            return self.content_answer
        elif type == "reference":
            return self.content_reference
        elif type == "suggested-question":
            return self.content_suggested_question
        else:
            raise TypeError(f"<无效的类型：{type}>")


a = {
    "type": 2,
    "invocationId": "0",
    "item": {
        "messages": [
            {
                "text": "使用以下Markdown模板为我总结专栏文章数据，除非文章中的内容无意义，或者内容较少无法总结，或者未提供文章数据，或者无有效内容，你就不使用模板回复，只回复“无意义”：## 概述        {内容，尽可能精简总结内容不要太详细}        ## 要点        - {使用不重复并合适的emoji，仅限一个，禁止重复} {内容不换行大于15字，可多项，条数与有效 内容数量呈正比}        不要随意翻译任何内容。仅使用中文总结。        不说与总结无关的其他内容，你的回复仅限固定格式提供的“概述”和“要点”两项。专栏标题为“专栏行为准则  \n        ”，专栏文章数据如下，立刻开始总结：专栏行 为准则,欢迎各位使用bilibili专栏，为了保证bilibili专栏的内容质量，维护专栏的内容生态，让创作者和读者都拥有良好的使用体验和阅读体验，请各位谨遵以下规范条例：,bilibili严格遵守我国政府颁布的《互联网信息服务管理办法》第十五条规定，并将此作为bilibili平台运行的基本准则；对于含有以下内容的信息，我们将视违规情节严重性封禁专栏权限，严 重者将导致您的账号被封停，并且我们还将保留追究相应的法律责任的权利：,(一)反对宪法所确定的基本原则的；,(二)危 害国家安全，泄露国家秘密，颠覆国家政权，破坏国家统一的；,(三)损害国家荣誉和利益的；,(四)煽动民族仇恨、民族歧 视，破坏民族团结的；,(五)破坏国家宗教政策，宣扬邪教和封建迷信的；,(六)散布谣言，扰乱社会秩序，破坏社会稳定的 ；,(七)散布淫秽、色情、赌博、暴力、凶杀、恐怖或者教唆犯罪的；,(八)侮辱或者诽谤他人，侵害他们合法权益的；,(九)含有法律、行政法规禁止的其他内容的。,为了保护用户创造的内容、维护良好的社区氛围，我们会对以下违禁行为进行处理，对相关稿件进行退回或锁定，同时将视违规情节严重性封禁专栏权限，情节特别严重参照严令禁止条例处理方式：,一、含有低俗、色情内容,文章中不允许含有性暗示类型的露骨内容，如色情描写、露点图片等。,禁止在文章及评论中发布与色情 内容有关的第三方网址、社交账号、网盘代码等违规信息。,二、涉及欺诈、诈骗行为,所有通过欺骗他人，为自己谋取经济 利益的行为都是不允许的。,三、人身攻击,请不要对任何个人或群体进行嘲讽、发布仇恨言论、挑拨他人矛盾。,四、侵犯个人隐私,文章内容涉嫌跟踪、威胁、骚扰、胁迫、侵犯用户个人隐私、披露用户个人信息等情况，将会受到严肃处理。,五、 恶意冒充他人,禁止通过自己的账号信息（昵称、头像、签名、个人空间等），恶意模仿特定用户。另外，伪装成涉及官方业务的账号，同样也是不允许的。,六、侵犯他人版权,未注明详细出处，在投稿中存在大量抄袭引用他人原创的文章内容；,未经原作者允许，以冒充原作者身份的方式，或以已获得转载授权为由，搬运转载他人的作品。,对于涉及以上侵权行为的用户，我们将严肃处理。,七、恶意投稿,请勿恶意规避审核检测，以任意漏洞提交含有违禁内容的文章。,对于诸如错区或题文不符等文章投稿，我们会打回并给予修改的建议方式。请勿无视管理员修改提示，多次反复提交或多次删稿重投。,一、不接受的内容类型,专栏欢迎并推广原创的内容投稿，不接受未授权的转载搬运。除了涉及违规内容外，同时不接受以下分类主题的文章投稿：时事政治、健康医疗、民族宗教，以及其他带有渲染社会负面现象，对于社会导向有误的文章。,另外同样不接受内容不完整、主题不清晰、排版格式混乱（无标点或无段落）等无法满足正常阅读体验的文章稿件。,※\xa0 目前仅接受中文、英文、日文三种语言的投稿。外语相关部分请尽量备注中文翻译哦。,二、不推荐的投稿类型,为了建立健康的创作环境与 良好的用户体验，除了违法违规和以上不适宜的内容外，我们也同样不推荐发布以下分类主题的投稿：短文资讯、情感鸡汤 、图集展示（美图壁纸、涂鸦手绘、表情斗图等），以及个人动态（随笔日记、晒物晒照、投稿预告等）。,个人动态等个性化内容建议使用“发布动态”的功能哟。,三、鼓励原创内容,哔哩哔哩专栏鼓励用户发布原创文章。作者在投稿时可以勾选原 创声明，相应的专栏会展示原创标识。,（关于原创标识）,勾选原创声明意味着作者承诺文章是本人独立创作，并愿意承担 一切相关责任。对于冒充原创的行为，我们将按照平台规范给予处罚，包括但不限于锁定相应文章、收回创作激励计划收益 、取消专栏投稿权限、封禁账号等。,勾选“原创文章”即代表您承诺该文章是由您本人（或持有该账号之组织）独立创作完成，且不属于以下三种情况：,1.歪曲、篡改、抄袭、剽窃他人创作而产生的作品，,2.转发、大量引用、未经授权进行改编、 翻译、注释、整理他人作品形成的内容，,3.通过其他侵犯著作权方式获得的内容。,在取得原作者同意后，对作品进行改编 、翻译、注释、整理等二次创作的，视同原创。,对二次创作作品进行改编、翻译、注释、整理的，应获得原作者及二次创作作品作者的同意。,哔哩哔哩专栏鼓励用户发布原创文章，完成原创声明的文章会展示原创标识，但哔哩哔哩专栏无法对原创声明的真实性进行核实。若您在进行原创声明后，被证明的确存在侵权、抄袭等违规行为，我们将按照平台规范从严处罚。 包括但不限于收回投稿权限，封禁相关账号等。,四、不允许的垃圾广告,为了保证用户的阅读体验，我们拒绝各类垃圾营销 广告！,以下行为会被视为散播垃圾广告信息，我们会对其进行相应处理：,（1）内容主题涉及商业产品、品牌活动、物品交易等推广，或与投稿者个人及文章内容无关的推广；,（2）散播各类游戏、社区的邀请码与相关链接；,（3）纯招聘类信息 等；,（4）金融理财产品广告，包含但不限于股票基金、虚拟货币、保险产品、培训课程的推销和荐购,（5）多个账号发布 同类内容的推广，且稿件内容重复、质量低下，或涉及标题封面党、错区刷版等其他恶意投稿行为,以上内容将会被退回要求修改或者锁定处理。对于多次涉及发布垃圾广告行为的用户，将直接视为垃圾营销账号，取消专栏的投稿权限。,五、不适宜的标题形式,为了保证bilibili专栏的文章内容质量，我们拒绝各种以过度夸张、耸动的标题和内容去吸引人眼球的行为，标题党的标题种类包括但不限于：,（1） 使用过度夸张的惊叹词；,（2）\xa0 断章取义歪曲事实真相；,（3）\xa0 故意营造悬念引人好奇；,（4）\xa0 捏造正文中不存在的人、物、情节；,（5）\xa0 题文不符，标题存在歧义。,以上内容我们建议作者修改完毕后再次提交，请勿不经修改重复提交或删除重投。,目前专栏开放了动画、游戏、影视、生活、兴趣、轻小说、科技七个分区。,热爱动画的小伙伴，可投稿海内外番剧动画、动态漫画、独立动画短片相关的作品推荐、解读杂谈、盘点资讯、制作技巧等类型文章。,动漫杂谈：,与动画、漫画有关的科普杂谈、深度解读、盘点推荐等相关文章。,动漫资讯：,与 动画、漫画有关的作品预告、业界资讯、职人访谈等相关文章。,动画技术：,与动画制作有关研究讨论、技术教学，或个人 学院派作品展示与分析等相关文章。,喜欢游戏的小伙伴们，可投稿单机联机、电子竞技、网络游戏、手机游戏、桌游棋牌相关的作品推荐、剧情解析、技巧攻略、业界杂谈等类型文章。,单机游戏：,以单机或其联机模式为主要内容的相关文章。,电子竞技：,电子竞技游戏项目为主要内容的相关文章。,手机游戏：,手机及平板设备平台上的游戏相关文章。,网络游戏：,多人在线游戏为主要内容的相关文章。,桌游棋牌：,桌游、棋牌、卡牌对战等为主要内容的相关文章。,在影视分区，小伙伴们可以发布你对影视作品内容的解读或推荐。不论是电影、电视剧，还是纪录片或综艺明星相关的文章，都可以在这里与大家 分享。,电影：,对电影作品内容的解读或推荐。,电视剧：,对电视剧作品内容的解读或推荐。,纪录片：,对纪录片作品内容 的解读或推荐。,综艺：,对国内外电视节目或网络自制的综艺类节目的解读或推荐。,这里是各种美食、萌宠的聚集地，还有许多时尚达人带你走在时尚前沿。热爱生活的你还能在这里找到运动攻略、或是享受闲散的日常时光。一定要来生活区看看 哦！,美食：,一切和食物相关的鉴赏或料理制作教程。,萌宠：,可爱的、萌萌哒的宠物相关文章。,时尚：,包括但不限于服 饰、化妆/护肤的推荐、分享和测评。,运动：,运动及健身项目相关的文章。,日常：,一般日常向的生活类文章。,你有什么 兴趣爱好吗？绘画、手工、摄影、音乐、舞蹈、模型手办，这是一个精彩纷呈的小世界。与小伙伴们分享你的爱好，和兴趣 相投的朋友交流技术经验。把你的最得意的作品和大家展示一下吧！,绘画：,绘画爱好者们关于绘画技巧、绘图过程的分享 交流场所。,手工：,简易手工艺品的diy制作教程，例如；折纸、手账、橡皮章等。,摄影：,摄影相关的器材、教程分享，摄影图集等。,音乐舞蹈：,以音乐、舞蹈为主要内容的相关文章。,模型手办：,模型手办的相关评测、美图分享、购买贴士等 。,欢迎大家将自己撰写的原创、同人小说等作品，分享给同样爱好阅读轻小说的小伙伴哦。同时，在“小说杂谈”分类中，您还可以分享出对各个书籍作品的推荐与读后感，和大家一起讨论写作技巧与喜爱的作者吧。下一个文豪就是您啦！,原创连载：,由创作者本人参与创作的、篇幅不低于2篇的小说作品。,同人连载：,对原有作品进行二次创作、篇幅不低于2篇的小说作品。,短篇小说：,篇幅仅限于1篇的小说，包括原创和同人作品。,小说杂谈：,写作技巧、读书心得、或书籍推荐等文章。, 如果你对科学技术、人文地理有一定的专业知识，可投稿相关的趣味科普向的文章。对3C数码与汽车有一定了解的兴趣的小 伙伴们，也可以投稿相关产品的测评推荐、原理知识、历史文化、使用或购买贴士等内容的文章，但不包括广告哦。,人文历史：,体现人文或历史的稿件，如民间文化传承、讲谈人文历史等。,自然：,具有科普性质的，与地球、宇宙、自然科学等相关的文章。,数码：,3C数码相关产品的测评推荐、原理知识、使用等文章。,汽车：,汽车、摩托车、公交车以及竞赛用车等 轮式交通工具相关。,学习：,技能演示及学习心得经验分享。",
                "author": "user",
                "from": {"id": "844425479597690", "name": None},
                "createdAt": "2023-04-28T15:45:21.5428787+00:00",
                "timestamp": "2023-04-28T15:45:21.5398446+00:00",
                "locale": "en-us",
                "market": "en-us",
                "region": "us",
                "messageId": "38aa19ae-9b4b-4ac0-b29b-915078efe45a",
                "requestId": "38aa19ae-9b4b-4ac0-b29b-915078efe45a",
                "nlu": {
                    "scoredClassification": {"classification": "DEEP_LEO", "score": None},
                    "classificationRanking": [{"classification": "DEEP_LEO", "score": None}],
                    "qualifyingClassifications": None,
                    "ood": None,
                    "metaData": None,
                    "entities": None,
                },
                "offense": "None",
                "feedback": {"tag": None, "updatedOn": None, "type": "None"},
                "contentOrigin": "cib",
                "privacy": None,
                "inputMethod": "Keyboard",
            },
            {
                "text": "## 概述\n这篇文章是bilibili专栏的行为准则，介绍了专栏的投稿规范、违禁内容、原创声明、垃圾 广告、标题党等方面的注意事项，以及各个分区的内容分类和要求。\n## 要点\n- 📜 专栏投稿需遵守《互联网信息服务管 理办法》第十五条规定，不得发布反对宪法、危害国家安全、破坏民族团结等违法违规内容。\n- 🚫 专栏不接受未授权的转载搬运，不接受时事政治、健康医疗、民族宗教等不适宜的内容，不接受含有低俗、色情、欺诈、诈骗、人身攻击、侵犯隐 私等违禁行为的内容。\n- ✍️ 专栏鼓励用户发布原创文章，勾选原创声明的文章会展示原创标识，但若存在侵权、抄袭等违规行为，将按照平台规范从严处罚。\n- 🚮 专栏拒绝各类垃圾营销广告，包括商业产品、品牌活动、物品交易等推广，以及游戏、社区的邀请码与相关链接等。\n- 📢 专栏拒绝各种以过度夸张、耸动的标题和内容去吸引人眼球的标题党行为，包括使用惊叹词、断章取义、营造悬念、捏造情节等。\n- 📚 专栏开放了动画、游戏、影视、生活、兴趣、轻小说、科技七个分区，每个分区有不同的内容分类和要求。",
                "author": "bot",
                "createdAt": "2023-04-28T15:45:35.7117896+00:00",
                "timestamp": "2023-04-28T15:45:35.7117896+00:00",
                "messageId": "c448e21b-2a9b-4695-addf-754d7d21c508",
                "requestId": "38aa19ae-9b4b-4ac0-b29b-915078efe45a",
                "offense": "None",
                "adaptiveCards": [
                    {
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": '[1]: https://www.bilibili.com/read/cv11396367 "教程/投稿专栏及修改 - 哔哩哔哩"\n[2]: https://zhidao.baidu.com/question/1868537216883827227.html "bilibili怎么看专栏_百度知道"\n[3]: https://www.bilibili.com/read/home "B站UP主专栏-个人空间-自媒体-哔哩哔哩官网"\n[4]: https://www.bilibili.com/read/cv403592/ "【bilibili专栏 × Markdown】撰写B站专栏的新方式 - 哔哩哔哩"\n\n## 概述\n这篇 文章是bilibili专栏的行为准则，介绍了专栏的投稿规范、违禁内容、原创声明、垃圾广告、标题党等方面的注意事项，以 及各个分区的内容分类和要求。\n## 要点\n- 📜 专栏投稿需遵守《互联网信息服务管理办法》第十五条规定，不得发布反 对宪法、危害国家安全、破坏民族团结等违法违规内容。\n- 🚫 专栏不接受未授权的转载搬运，不接受时事政治、健康医疗、民族宗教等不适宜的内容，不接受含有低俗、色情、欺诈、诈骗、人身攻击、侵犯隐私等违禁行为的内容。\n- ✍️ 专栏鼓励用户发布原创文章，勾选原创声明的文章会展示原创标识，但若存在侵权、抄袭等违规行为，将按照平台规范从严处罚。\n- 🚮 专栏拒绝各类垃圾营销广告，包括商业产品、品牌活动、物品交易等推广，以及游戏、社区的邀请码与相关链接等。\n- 📢 专栏拒绝各种以过度夸张、耸动的标题和内容去吸引人眼球的标题党行为，包括使用惊叹词、断章取义、营造悬念、 捏造情节等。\n- 📚 专栏开放了动画、游戏、影视、生活、兴趣、轻小说、科技七个分区，每个分区有不同的内容分类和要求。',
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "size": "small",
                                "text": "Learn more: [1. www.bilibili.com](https://www.bilibili.com/read/cv11396367) [2. zhidao.baidu.com](https://zhidao.baidu.com/question/1868537216883827227.html) [3. www.bilibili.com](https://www.bilibili.com/read/home) [4. www.bilibili.com](https://www.bilibili.com/read/cv403592/)",
                                "wrap": True,
                            },
                        ],
                    }
                ],
                "sourceAttributions": [
                    {
                        "providerDisplayName": "教程/投稿专栏及修改 - 哔哩哔哩",
                        "seeMoreUrl": "https://www.bilibili.com/read/cv11396367",
                        "searchQuery": "bilibili专栏",
                    },
                    {
                        "providerDisplayName": "bilibili怎么看专栏_百度知道",
                        "seeMoreUrl": "https://zhidao.baidu.com/question/1868537216883827227.html",
                        "searchQuery": "bilibili专栏",
                    },
                    {
                        "providerDisplayName": "B站UP主专栏-个人空间-自媒体-哔哩哔 哩官网",
                        "seeMoreUrl": "https://www.bilibili.com/read/home",
                        "imageLink": "https://bing.com/th?id=OIP.VmM4ObzSaEzBBcWNPV7CcAHaCT&pid=cdx",
                        "imageWidth": "1360",
                        "imageHeight": "424",
                        "imageFavicon": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGuSURBVFhH5ZaxTsMwEIY9INhgBfFE5SWQYAaehZGpDl0QO6ydEANDQYotUYkNUQlGGGAqd45dHP8OTtQ6QuKTTo3+O9/vulF94m8yHq8JqaQo1KuQ+kKMpps20x5ew2ulejO9uGdrCr1PMV+EVDedNmHMaY3fg3u2plAHweL2m4ibz8W5OrQVLbgs16NNWDt72rJVSJM5a9yzE781i22iaz3AOxyqYzr+W3p53qHRsmF6Um/2gNOQj7tUNIFF+WJiPA28m37Nq5D6XpxON+iNL4+iBb0EeZvfpZ64FiO9Ux3PCuGe3LvmRd50FF81MYe5o9qEv4FP/tfzBIrcgB8ImQE/EAKkGlC82BhYtZlUPfiBEMCNXI6fU6TqXc4FCgGpfEiqHvIgBKTyIal6yIMQ4B9poWdWbSZV/5OrAoWAQu2RPqPPZ/OcIlUPfiBkBvxAyAz4gZAZ8AMhM+DX52U0LLdrXjwl0Ztav46lvjKFq4YnIO7te5nr2MyBvthjsLcZi3g8ihVkDfVQjWTuePqcC/kLL4ZSBw+nUp1Q3FHBR3ThMsE9TW/ygLH8/yLEN50olbkkOCVHAAAAAElFTkSuQmCC",
                        "searchQuery": "bilibili专栏",
                    },
                    {
                        "providerDisplayName": "【bilibili专栏 × Markdown】撰写B站专栏的新方式 - 哔哩哔哩",
                        "seeMoreUrl": "https://www.bilibili.com/read/cv403592/",
                        "imageLink": "https://bing.com/th?id=OIP.xF74GZrgoBaQQfuBLkFxwwHaFI&pid=cdx",
                        "imageWidth": "1096",
                        "imageHeight": "759",
                        "imageFavicon": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGuSURBVFhH5ZaxTsMwEIY9INhgBfFE5SWQYAaehZGpDl0QO6ydEANDQYotUYkNUQlGGGAqd45dHP8OTtQ6QuKTTo3+O9/vulF94m8yHq8JqaQo1KuQ+kKMpps20x5ew2ulejO9uGdrCr1PMV+EVDedNmHMaY3fg3u2plAHweL2m4ibz8W5OrQVLbgs16NNWDt72rJVSJM5a9yzE781i22iaz3AOxyqYzr+W3p53qHRsmF6Um/2gNOQj7tUNIFF+WJiPA28m37Nq5D6XpxON+iNL4+iBb0EeZvfpZ64FiO9Ux3PCuGe3LvmRd50FF81MYe5o9qEv4FP/tfzBIrcgB8ImQE/EAKkGlC82BhYtZlUPfiBEMCNXI6fU6TqXc4FCgGpfEiqHvIgBKTyIal6yIMQ4B9poWdWbSZV/5OrAoWAQu2RPqPPZ/OcIlUPfiBkBvxAyAz4gZAZ8AMhM+DX52U0LLdrXjwl0Ztav46lvjKFq4YnIO7te5nr2MyBvthjsLcZi3g8ihVkDfVQjWTuePqcC/kLL4ZSBw+nUp1Q3FHBR3ThMsE9TW/ygLH8/yLEN50olbkkOCVHAAAAAElFTkSuQmCC",
                        "searchQuery": "bilibili专栏",
                    },
                ],
                "feedback": {"tag": None, "updatedOn": None, "type": "None"},
                "contentOrigin": "DeepLeo",
                "privacy": None,
                "suggestedResponses": [
                    {
                        "text": "谢谢你的总结，很清晰明了。",
                        "author": "user",
                        "createdAt": "2023-04-28T15:46:21.414498+00:00",
                        "timestamp": "2023-04-28T15:46:21.414498+00:00",
                        "messageId": "fb5b2564-ea8f-4916-a594-c1a04ac12715",
                        "messageType": "Suggestion",
                        "offense": "Unknown",
                        "feedback": {"tag": None, "updatedOn": None, "type": "None"},
                        "contentOrigin": "DeepLeo",
                        "privacy": None,
                    },
                    {
                        "text": "你能不能给我一些bilibili专栏的优秀文章推荐？",
                        "author": "user",
                        "createdAt": "2023-04-28T15:46:21.4144999+00:00",
                        "timestamp": "2023-04-28T15:46:21.4144999+00:00",
                        "messageId": "ec4d1fba-f600-4759-b12f-783020213cb4",
                        "messageType": "Suggestion",
                        "offense": "Unknown",
                        "feedback": {"tag": None, "updatedOn": None, "type": "None"},
                        "contentOrigin": "DeepLeo",
                        "privacy": None,
                    },
                    {
                        "text": "你对bilibili专栏的行为准则有什么看法？",
                        "author": "user",
                        "createdAt": "2023-04-28T15:46:21.4145003+00:00",
                        "timestamp": "2023-04-28T15:46:21.4145003+00:00",
                        "messageId": "e7c5c580-d339-48ad-802c-a0b097f78193",
                        "messageType": "Suggestion",
                        "offense": "Unknown",
                        "feedback": {"tag": None, "updatedOn": None, "type": "None"},
                        "contentOrigin": "DeepLeo",
                        "privacy": None,
                    },
                ],
                "spokenText": "专栏 开放了动画、游戏、影视、生活、兴趣、轻小说、科技七个分区，每个分区有不同的内容分类和要求",
            },
        ],
        "firstNewMessageIndex": 1,
        "defaultChatName": None,
        "conversationId": "51D|BingProd|249A1FE5B392941D813E03A279F80D097EB6D2AFE435C33C837A7ED2534C051C",
        "requestId": "38aa19ae-9b4b-4ac0-b29b-915078efe45a",
        "conversationExpiryTime": "2023-04-28T21:46:21.5020375Z",
        "shouldInitiateConversation": True,
        "telemetry": {"metrics": None, "startTime": "2023-04-28T15:45:21.5400683Z"},
        "throttling": {"maxNumUserMessagesInConversation": 20, "numUserMessagesInConversation": 1},
        "result": {"value": "Success", "message": "bilibili专栏", "serviceVersion": "20230427.71"},
    },
}
