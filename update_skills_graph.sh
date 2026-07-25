#!/bin/bash
# Skills 知识图谱更新脚本
# 在安装/删除新 skill 后运行，刷新交互式图谱

set -e
VAULT="$HOME/.hermes/skills-graph"

echo "✦ 更新 Skills 知识图谱..."
echo ""

# Step 1: 扫描所有 skill 元数据
echo "📡 Step 1/3: 扫描 Skills..."
python3 "$VAULT/analyze_skills.py" 2>&1 | grep -E "^(  |总计|分类|热门|报告)"

# Step 2: 生成交互图谱
echo ""
echo "🎨 Step 2/3: 生成 D3 交互图谱..."
python3 "$VAULT/build_graph_viz.py" 2>&1

echo ""
echo "✅ 更新完成！"
echo ""
echo "📂 产物位置:"
echo "  skills_knowledge_graph.html  — 交互图谱（浏览器打开）"
echo "  skills_analysis.json         — 完整数据"
echo "  skills_graph.json            — 图谱边/节点"
echo ""
echo "💡 也可以直接用 Graphify 查:"
echo "  graphify query '技能用途' --graph $VAULT/skills_graph.json"
