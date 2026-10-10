# 战后经济与金融史

从布雷顿森林体系到当代政策转向，追踪国际经济金融制度、重大危机及中国经济改革。重点解释事件的起因、政策的选择与执行、风险传播，以及不同国家和社会群体承担的后果。

[全书目录](textbook/README.md) · [编写标准](AGENTS.md) · [真实进度与审阅记录](reviews/progress.md)

全书十篇六十章已完成编写与本轮审阅。正文约66.8万汉字；含各章练习与答案约72.4万汉字，目录、来源账和审阅记录另计。每篇末章有完整比较实作及参考示范。逐章内容、关键来源及跨篇接口的核查证据见[最终验收记录](reviews/editorial-audit.md)。

正文使用逐章 Markdown 文件。历史主体截至2024年，较近变化在可靠资料支持下单列日期讨论。阅读站采用与 us-econ 相同的 VitePress 和 GitHub Actions 发布方式。


## 在线阅读与本地运行

- [在线教材](https://fangpings.github.io/economic-history/)
- [GitHub 仓库](https://github.com/fangpings/economic-history)

使用 Node.js 22，运行 `npm ci` 安装依赖，`npm run dev` 本地阅读，`npm run check` 核查教材结构，`npm run build` 生成网站，`npm run check:rendered` 检查生成页面的链接与锚点。推送到 `main` 后由 GitHub Actions 构建并发布 GitHub Pages。
