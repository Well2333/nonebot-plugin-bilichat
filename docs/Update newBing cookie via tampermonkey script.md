# 通过 tampermonkey 脚本更新网站 cookie

首先，你需要配置对应站点的 cookie 和 cookie_api 两项，并且将 HOST 设置为 `0.0.0.0` 以监听外部响应，例如

```env
HOST=0.0.0.0
PORT=8080

# bilibili
bilichat_bilibili_cookie=bilibili_cookies.json
bilichat_bilibili_cookie_api="/bilibili_cookie/"

# newbing
bilichat_newbing_cookie=cookies.json
bilichat_newbing_cookie_api="/newbing_cookie/"
```

然后，在启动 bot 后你应该可以看到如下日志

```log
06-30 22:39:16 [INFO] nonebot_plugin_bilichat | Setup bilibili cookies update api at http://0.0.0.0:8080/bilibili_cookie/
06-30 22:39:16 [INFO] nonebot_plugin_bilichat | Setup newbing cookies update api at http://0.0.0.0:8080/newbing_cookie/
```

这时对应站点 cookie 的升级 api 便架设完毕了，此时将以下脚本添加至你的 tampermonkey 中，更换对应的匹配站点，并填入对应的 api 地址

```javascript
// ==UserScript==
// @name         Cookie Extractor
// @namespace    yournamespace
// @version      1.0
// @description  Extracts cookies and sends them to 127.0.0.1:8080
// @match        " === 匹配的站点 === "
// @grant        GM_xmlhttpRequest
// ==/UserScript==

// Bing的站点替换为
// @match        *://www.bing.com/*
// BiliBili的站点(仅主页生效)替换为
// @match        *://www.bilibili.com

(function () {
  "use strict";

  // 提取所有的 cookies
  function getCookies() {
    var cookies = document.cookie.split("; ");
    var cookieObj = {};
    for (const element of cookies) {
      var cookie = element.split("=");
      var cookieName = cookie[0];
      var cookieValue = cookie[1];
      cookieObj[cookieName] = cookieValue;
    }
    return cookieObj;
  }

  // 发送 cookies 到指定的地址
  function sendCookies(cookies) {
    GM_xmlhttpRequest({
      method: "POST",
      url: "=== 填入你的发送地址 ===",
      headers: {
        "Content-Type": "application/json;charset=UTF-8"
      },
      data: JSON.stringify(cookies),
    });
  }

  // 主函数
  function main() {
    var cookies = getCookies();
    sendCookies(cookies);
  }

  // 执行主函数
  main();
})();
```

第一次使用打开对应的主页时，tampermonkey会弹出xhr安全请求的界面，点击总是允许即可，如想删除该xhr请求域白名单，需要进入油猴管理器找到该插件，点击设置，往下找到xhr安全，可以在用户域名白名单中找到你设置的ip/域名

在一切配置完成，打开对应的主页后，如果一切顺利的话，你应该可以看到以下日志

```log
06-30 22:49:02 [INFO] nonebot_plugin_bilichat | Successfully updated newbing cookies
06-30 22:49:02 [INFO] uvicorn | 127.0.0.1:10026 - "POST /newbing_cookie/ HTTP/1.1" 200
```

这样你的 cookies 就更新成功了
