# Hermes Skills 知识图谱 ✦

Hermes Agent 已安装 Skills 的交互式知识图谱。帮助你在 550+ 技能中快速找到需要的工具。

## 文件说明

| 文件 | 用途 |
|------|------|
| `skills_knowledge_graph.html` | 🎯 **交互式 D3 力导向图谱** — 直接浏览器打开 |
| `analyze_skills.py` | 扫描所有 SKILL.md，提取元数据，生成分析 JSON |
| `build_graph_viz.py` | 基于分析数据，生成 D3 交互图谱 HTML |
| `update_skills_graph.sh` | **一键更新脚本** — 安装/删除 skill 后刷新图谱 |

## 使用

```bash
# 更新图谱（装/删 skill 后执行）
bash update_skills_graph.sh

# 或用 Graphify 查询
graphify query "发公众号用什么？" --graph skills_graph.json
```

## 前置依赖

- Python 3
- graphifyy（可选，用于 query 命令）
- 浏览器（打开 HTML 图谱）
