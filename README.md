# 读文献（du-wen-xian）

**Reading Literature** — 一个Skill：拆解、精读、分析学术文献，并输出结构化精读报告（信息无损、逐节覆盖、零幻觉）的完整执行协议。当前版本 **v1.2.1**（交付物为纯文本Markdown）。

## 它做什么

给它一篇论文，它按固定协议产出一份“不读原文也不损失信息”的精读报告：

```
标题 → 导语（知识网络定位 + 作者谱系）
     → 摘要 → 引言 → 文献回顾 → 研究设计 → 实证分析 → 讨论与结论
```

它会从引言、文献回顾、研究设计、实证分析、结论与讨论等论文的每个版块挑选关键段落，按 **「外文原文 + 中文译文 + 详细解析」** 三段式领读，报告收尾附术语中英文对照表、800字文献主旨大意提炼、思考问题（理解 / 批判 / 延伸三层）与覆盖自查表。

## 功能亮点

- **全文领读协议（v1.2.0 新增）**：ai会先通读全文一遍，依据使用者过往对话历史判断其知识背景与研究偏好，对引言、文献回顾、研究设计、实证分析、讨论与结论五大结构部分逐一挑选关键必读段落领读——领读一遍后，即使不读原文全文也能基本掌握文献内容、不遗漏知识点。
- **三层精读法**：结构读 → Keshav 三遍法（含五C自检）→ 分层精读。
- **阅读密码表（Shon 14密码）**：WTD / SPL / CPL / GAP / RAT / ROF / RCL / RTC / WTDD / RFW / POC / MOP / RPP / WIL，逐句标注论证功能，配RCOS整合表。
- **论证解剖五要素（Booth）**：claim / reasons / evidence / warrant / acknowledgment & response，配证据五标准与warrant五问。
- **定量论文精读十一条（Krippner / ASA）**与**质性研究质量评估（CASP十问）**，按文献类型自动路由。
- **零幻觉铁律**：精读层严格限于所读文档既有内容，不编造、不推测作者动机；导读层（文献外背景）一律经WebSearch核实并明示标注。
- **个性化资产对接**：基于使用者研究画像，逐条标注每个批评点 / 遗漏点 / 待探讨问题可对接自己的哪条研究线、哪篇稿件。

## 安装（Codex; WorkBuddy; Zcode; Trae）
在对话中输入：
帮我安装这个skill: https://github.com/BenjaminXi66/du-wen-xian

## 目录结构

```
├── SKILL.md              # 技能主协议（铁律、精读顺序、全文领读协议、九步执行流程）
├── chapters/             # 12章方法论（三层精读法、阅读密码表、论证解剖、
│                         # 来源甄别、笔记组织、专著精读、引用规范、报告模板、日课、导读层协议）
├── references/
│   └── sources.md        # 七份方法来源的完整书目与取材映射
├── glossary.md           # 术语与阅读密码速查
├── patterns.md           # 可操作技巧清单
└── cheatsheet.md         # 决策规则与阈值速查
```

## 方法来源

Wayne C. Booth 等《The Craft of Research》(4th ed.)、Phillip C. Shon《会读才会写》、S. Keshav《How to Read a Paper》、Frederique Laubepin《How to Read (and Understand) a Social Science Journal Article》、Greta Krippner《How to Read a (Quantitative) Journal Article》(ASA)、CASP Qualitative Checklist (2024)、董晨宇《拆论文》。完整书目见 [references/sources.md](references/sources.md)。

## 许可证

[MIT](LICENSE)
