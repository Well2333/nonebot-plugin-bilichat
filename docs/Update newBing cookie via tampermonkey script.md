# 通过 tampermonkey 脚本更新 newbing cookie

首先，你需要配置 bilichat_newbing_cookie 和 bilichat_newbing_cookie_api 两项，并且将 HOST 设置为 `0.0.0.0` 以监听外部响应，例如

```env
HOST=0.0.0.0
PORT=8080

bilichat_newbing_cookie=cookies.json
bilichat_newbing_cookie_api="/newbing_cookie/"
```

然后，在启动 bot 后你应该可以看到如下日志

```log
06-30 22:39:16 [INFO] nonebot_plugin_bilichat | Setup newbing cookies update api at http://0.0.0.0:8080/newbing_cookie/
```

这时 newbing cookie 的升级 api 便架设完毕了，此时将以下脚本添加至你的 tampermonkey 中，并填入对应的 api 地址

```javascript
// ==UserScript==
// @name         Cookie Extractor
// @namespace    yournamespace
// @version      1.0
// @description  Extracts cookies and sends them to 127.0.0.1:8080
// @match        *://www.bing.com/*
// @grant        none
// ==/UserScript==

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
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:8080/newbing_cookie/", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(cookies));
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

打开任意的 [非中国区 Bing 网页](https://www.bing.com/search?q=Bing+AI&showconv=1)，如果一切顺利的话，你应该可以看到以下日志

```log
06-30 22:49:02 [INFO] nonebot_plugin_bilichat | Successfully updated newbing cookies
06-30 22:49:02 [INFO] uvicorn | 127.0.0.1:10026 - "POST /newbing_cookie/ HTTP/1.1" 200
```

这样你的 newbing 就更新成功了，在下次重启或 newbing 失败重试时即可应用
