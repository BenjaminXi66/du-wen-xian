#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_mindmap.py — 从缩进大纲生成全中文思维导图 PNG（renwen-sheke-du-wenxian v1.1）

用法:
    python render_mindmap.py outline.txt -o 思维导图.png
    python render_mindmap.py outline.txt -o out.png --width-chars 12 --dpi 200

大纲格式:
    - 缩进文本: 每级 2 个空格或 1 个 Tab
    - 兼容 Markdown 列表(- / * / 1.) 与 # 标题前缀
    - 首行 = 中心主题; 若出现多个顶层节点, 自动补一个根节点

依赖: matplotlib (pip install matplotlib)
"""
import argparse
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from matplotlib import font_manager
except ImportError:
    sys.exit("缺少 matplotlib，请先安装：pip install matplotlib")


# ---------------------------------------------------------------- 大纲解析

def parse_outline(text):
    """把缩进大纲解析为 (depth, text) 列表，深度由缩进自动归一。"""
    items = []  # (raw_indent, text)
    for raw in text.splitlines():
        line = raw.rstrip("\n").rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.lstrip()
        # 去掉 markdown 标题号与列表符
        s = s.lstrip("#").strip()
        for m in ("- ", "* ", "• ", "+ "):
            if s.startswith(m):
                s = s[len(m):]
                break
        s = s.strip()
        if not s:
            continue
        items.append((indent, s))
    if not items:
        sys.exit("大纲为空：请提供至少一行的缩进大纲")

    # 归一化深度：维护一个缩进栈
    depths, stack = [], []
    for indent, txt in items:
        while stack and indent < stack[-1]:
            stack.pop()
        if not stack or indent > stack[-1]:
            stack.append(indent)
        depths.append(len(stack) - 1)
    return list(zip(depths, [t for _, t in items]))


def build_tree(pairs):
    """(depth, text) 列表 → 嵌套树。多个根时自动补根。"""
    roots = []
    stack = []  # (depth, node)
    for depth, txt in pairs:
        node = {"text": txt, "children": []}
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1]["children"].append(node)
        else:
            roots.append(node)
        stack.append((depth, node))
    if len(roots) == 1:
        return roots[0]
    return {"text": "思维导图", "children": roots}


# ---------------------------------------------------------------- 布局

PALETTE = ["#DCE9F7", "#DCEFE1", "#FBF0DC", "#EFE6F7", "#FBDFDF", "#D8F0EF", "#F1EDE2"]
EDGE = "#7C8AA0"
TEXT = "#1F2937"


def wrap(text, width):
    """按显示宽度换行：CJK 逐字可断，英文/数字按整词不断行。"""
    import re
    # 词元：英文/数字整词 | 空格 | 其余单字符（CJK 等）
    tokens = re.findall(r"[A-Za-z0-9]+(?:[-'./][A-Za-z0-9]+)*|\s|.", text)
    lines, cur, cur_w = [], "", 0
    for tok in tokens:
        if tok.isspace():
            if cur_w + 1 > width and cur.strip():
                lines.append(cur.rstrip())
                cur, cur_w = "", 0
            elif cur:
                cur += " "
                cur_w += 1
            continue
        w = sum(2 if ord(c) > 0x2E7F else 1 for c in tok)
        if cur_w + w > width and cur.strip():
            lines.append(cur.rstrip())
            cur, cur_w = "", 0
        cur += tok
        cur_w += w
    if cur.strip():
        lines.append(cur.rstrip())
    return "\n".join(lines) or text


def layout(node, depth, counter, positions, max_depth_box):
    """中序遍历：叶子按顺序取 y，内部节点取子节点均值。返回叶子行数。"""
    node["_d"] = depth
    node["_wrapped"] = wrap(node["text"], ARGS.width_chars)
    nlines = node["_wrapped"].count("\n") + 1
    node["_h"] = 0.52 + 0.28 * (nlines - 1)          # 框高
    node["_w"] = 3.0 if depth == 0 else (2.6 if depth == 1 else 2.3)
    if node["children"]:
        ys = []
        for c in node["children"]:
            ys.append(layout(c, depth + 1, counter, positions, max_depth_box))
        node["_y"] = sum(ys) / len(ys)
        return node["_y"]
    y = counter[0]
    counter[0] += 1
    node["_y"] = -y
    return node["_y"]


def draw(node, ax):
    x = node["_d"] * ARGS.col_width
    box = FancyBboxPatch(
        (x, node["_y"] - node["_h"] / 2), node["_w"], node["_h"],
        boxstyle="round,pad=0.06,rounding_size=0.10",
        facecolor=PALETTE[node["_d"] % len(PALETTE)],
        edgecolor=EDGE, linewidth=1.1, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + node["_w"] / 2, node["_y"], node["_wrapped"],
            ha="center", va="center", fontsize=ARGS.font_size,
            color=TEXT, zorder=3, linespacing=1.25)

    for c in node["children"]:
        cx = c["_d"] * ARGS.col_width
        x0, y0 = x + node["_w"], node["_y"]
        x1, y1 = cx, c["_y"]
        mid = x0 + (x1 - x0) * 0.45
        ax.plot([x0, mid, mid, x1], [y0, y0, y1, y1],
                color=EDGE, linewidth=1.0, zorder=1, solid_capstyle="round")
        draw(c, ax)


# ---------------------------------------------------------------- 主流程

def pick_cjk_font():
    candidates = ["Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC",
                  "Source Han Sans SC", "WenQuanYi Micro Hei", "Arial Unicode MS"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    sys.exit("未找到中文字体（已尝试：%s）。请安装微软雅黑或思源黑体后重试。" % ", ".join(candidates))


def main():
    global ARGS
    p = argparse.ArgumentParser(description="缩进大纲 → 全中文思维导图 PNG")
    p.add_argument("outline", help="大纲文本文件路径")
    p.add_argument("-o", "--output", default="mindmap.png", help="输出 PNG 路径")
    p.add_argument("--width-chars", type=int, default=12, help="节点内每行换行宽度（半角宽）")
    p.add_argument("--col-width", type=float, default=3.6, help="层间横向间距")
    p.add_argument("--font-size", type=float, default=10.5, help="节点字号")
    p.add_argument("--dpi", type=int, default=200, help="输出分辨率")
    ARGS = p.parse_args()

    with open(ARGS.outline, "r", encoding="utf-8") as f:
        pairs = parse_outline(f.read())
    tree = build_tree(pairs)

    matplotlib.rcParams["font.family"] = pick_cjk_font()
    matplotlib.rcParams["axes.unicode_minus"] = False

    positions = {}
    counter = [0]
    layout(tree, 0, counter, positions, None)
    leaf_count = counter[0]
    max_depth = max(n["_d"] for n in iter_nodes(tree))

    fig_w = (max_depth + 1) * ARGS.col_width + 1.0
    fig_h = max(leaf_count * 0.85, 3.0)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(-0.4, (max_depth + 1) * ARGS.col_width + 3.2)
    ax.set_ylim(-leaf_count - 0.4, 0.8)
    ax.axis("off")

    draw(tree, ax)
    fig.savefig(ARGS.output, dpi=ARGS.dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.25)
    print("已生成：%s（%d 个节点）" % (ARGS.output, count_nodes(tree)))


def iter_nodes(node):
    yield node
    for c in node["children"]:
        yield from iter_nodes(c)


def count_nodes(node):
    return sum(1 for _ in iter_nodes(node))


if __name__ == "__main__":
    main()
