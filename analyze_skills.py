#!/usr/bin/env python3
"""Analyze all installed Hermes skills, extract metadata, and build relationship graph."""
import os, sys, json, re
from pathlib import Path
from collections import defaultdict, Counter

SKILLS_DIR = Path(os.path.expanduser("~/.hermes/skills"))
OUT_DIR = Path(os.path.expanduser("~/.hermes/skills-graph"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Categories inferred from descriptions and directory names + hub taxonomy
CATEGORY_MAP = {
    "ai-berkshire": "价值投资 - 巴菲特/芒格",
    "ai-radar": "AI资讯",
    "aihot": "AI资讯",
    "ai-article-daily": "AI资讯",
    "a-stock-data": "A股金融数据",
    "mx-data": "A股金融数据",
    "mx-search": "A股金融数据",
    "mx-xuangu": "A股金融数据",
    "mx-zixuan": "A股金融数据",
    "mx-moni": "A股金融数据",
    "hithink_finance": "A股金融数据",
    "gf_stock_valuation": "A股金融数据",
    "wen-cai": "A股金融数据",
    "alice-stock-trading-strategy": "A股金融数据",
    "financial-report": "金融报告",
    "stock-feed": "A股金融数据",
    "financial-tycoon": "金融交易分析",
    "baoyu-image-gen": "AI图像生成",
    "baoyu-cover-image": "AI图像生成",
    "baoyu-comic": "漫画与插画",
    "baoyu-article-illustrator": "漫画与插画",
    "baoyu-infographic": "信息图",
    "baoyu-slide-deck": "幻灯片",
    "baoyu-diagram": "图表与架构图",
    "baoyu-design": "设计与UI",
    "baoyu-markdown-to-html": "内容发布",
    "baoyu-post-to-wechat": "内容发布",
    "baoyu-post-to-weibo": "内容发布",
    "baoyu-post-to-x": "内容发布",
    "baoyu-translate": "翻译与多语言",
    "baoyu-format-markdown": "文档工具",
    "baoyu-url-to-markdown": "文档工具",
    "baoyu-danger-x-to-markdown": "文档工具",
    "baoyu-youtube-transcript": "视频处理",
    "baoyu-wechat-summary": "内容分析",
    "baoyu-xhs-images": "内容发布",
    "baoyu-compress-image": "图像处理",
    "baoyu-electron-extract": "逆向工程",
    "baoyu-danger-gemini-web": "AI图像生成",
    "canghe-image-gen": "AI图像生成",
    "canghe-cover-image": "AI图像生成",
    "canghe-comic": "漫画与插画",
    "canghe-article-illustrator": "漫画与插画",
    "canghe-slide-deck": "幻灯片",
    "canghe-markdown-to-html": "内容发布",
    "canghe-post-to-wechat": "内容发布",
    "canghe-post-to-x": "内容发布",
    "canghe-seedance-video": "AI视频生成",
    "canghe-manga-drama": "AI视频生成",
    "canghe-manga-style-video": "AI视频生成",
    "canghe-gpt-image": "AI图像生成",
    "canghe-tianyancha": "企业信息",
    "canghe-xhs-images": "内容发布",
    "canghe-url-to-markdown": "文档工具",
    "canghe-format-markdown": "文档工具",
    "canghe-compress-image": "图像处理",
    "canghe-danger-gemini-web": "AI图像生成",
    "canghe-danger-x-to-markdown": "文档工具",
    "canghe-douyin-downloader": "视频下载",
    "canghe-volcengine-video-understanding": "视频处理",
    "gpt-image-2-prompt": "AI图像生成",
    "image-gen": "AI图像生成",
    "seedance-video-gen": "AI视频生成",
    "seedream-5-0-lite": "AI图像生成",
    "nonelinear-image-gen": "AI图像生成",
    "nonelinear-text": "AI文本生成",
    "nonelinear-vision": "多模态分析",
    "openai-image": "AI图像生成",
    "multi-agent-image": "AI图像生成",
    "cf-image-generation": "AI图像生成",
    "qianwen-image-generation": "AI图像生成",
    "qianwen-video-generation": "AI视频生成",
    "book-illustration-workflow": "漫画与插画",
    "douyin-works-crawler": "社媒数据分析",
    "douyin-search": "社媒数据分析",
    "douyin-hot-trend": "社媒数据分析",
    "douyin-realtime-search": "社媒数据分析",
    "douyin-subscribe": "社媒数据分析",
    "douyin-top-account": "社媒数据分析",
    "douyin-rise-ranking": "社媒数据分析",
    "douyin-similar-account": "社媒数据分析",
    "douyin-account-diagnosis": "社媒数据分析",
    "douyin-ai-feed": "社媒数据分析",
    "douyin-comment": "社媒数据分析",
    "douyin-content-surge": "社媒数据分析",
    "douyin-daily-hot": "社媒数据分析",
    "douyin-weekly-surge": "社媒数据分析",
    "douyin-prohibited-word": "社媒数据分析",
    "douyin-search": "社媒数据分析",
    "douyin-subscribe": "社媒订阅",
    "wechat-search": "公众号数据分析",
    "wechat-10w-hot": "公众号数据分析",
    "wechat-original-hot": "公众号数据分析",
    "wechat-title": "公众号数据分析",
    "wechat-cover": "公众号数据分析",
    "wechat-fastest-growing": "公众号数据分析",
    "wechat-top-account": "公众号数据分析",
    "wechat-prohibited-word": "公众号数据分析",
    "wechat-rewrite": "公众号数据分析",
    "wechat-write": "公众号数据分析",
    "wechat-similar-account": "公众号数据分析",
    "wechat-account-analyzer": "公众号数据分析",
    "wechat-channels-ai-feed": "公众号数据分析",
    "gzh-ai-feed": "公众号数据分析",
    "gzh-astock-top": "公众号数据分析",
    "gzh-search-crawler": "公众号数据分析",
    "gzh-history-crawler": "公众号数据分析",
    "gzh-subscribe": "公众号订阅",
    "xiaohongshu-search": "小红书数据分析",
    "xiaohongshu-crawler": "小红书数据分析",
    "xiaohongshu-cover": "小红书数据分析",
    "xiaohongshu-title": "小红书数据分析",
    "xiaohongshu-rewrite": "小红书数据分析",
    "xiaohongshu-write": "小红书数据分析",
    "xiaohongshu-account-analyzer": "小红书数据分析",
    "xiaohongshu-ai-feed": "小红书数据分析",
    "xiaohongshu-top-account": "小红书数据分析",
    "xiaohongshu-dailytop": "小红书数据分析",
    "xiaohongshu-lowtop": "小红书数据分析",
    "xiaohongshu-weeklytop": "小红书数据分析",
    "xiaohongshu-prohibited-word": "小红书数据分析",
    "xiaohongshu-similar-account": "小红书数据分析",
    "xiaohongshu-note-analyzer": "小红书数据分析",
    "xiaohongshu-title-score": "小红书数据分析",
    "bili-ai-feed": "B站数据分析",
    "bilibili-viral-topic": "B站数据分析",
    "bilibili-portfolio-search": "B站数据分析",
    "B站关键词搜作品": "B站数据分析",
    "trending-hub": "热搜聚合",
    "trending-hub-top10": "热搜聚合",
    "multi-content-feed": "多平台创作",
    "multi-rewrite": "多平台创作",
    "multi-wordcheck": "多平台创作",
    "video-downloader": "视频下载",
    "douyin-prohibited-word": "多平台创作",
    "kangaroo-video-downloader": "视频下载",
    "huashu-douyin-script": "视频创作",
    "huashu-video-outline": "视频创作",
    "huashu-video-check": "视频创作",
    "huashu-article-to-x": "多平台创作",
    "huashu-data-pro": "数据分析与报告",
    "huashu-design": "设计",
    "huashu-slides": "幻灯片",
    "huashu-md-to-pdf": "文档工具",
    "huashu-info-search": "信息搜索",
    "huashu-material-search": "素材搜索",
    "huashu-research": "研究调研",
    "huashu-topic-gen": "内容创作",
    "huashu-prompt-save": "Prompt管理",
    "huashu-proofreading": "内容审校",
    "huashu-speech-coach": "演讲培训",
    "huashu-image-upload": "图像处理",
    "huashu-script-polish": "视频创作",
    "huashu-article-edit": "内容编辑",
    "huashu-xhs-image": "小红书创作",
    "huashu-wechat-image": "公众号创作",
    "tz-302ai-cli": "AI多媒体生成",
    "zero-302ai-cli": "AI多媒体生成",
    "edge-tts": "语音合成",
    "doubao-asr": "语音识别",
    "doubao-podcast": "语音合成",
    "doubao-voice": "语音合成",
    "doubao-voice-clone": "声音克隆",
    "doubao-multimodal-pipeline": "语音处理",
    "fish-tts": "语音合成",
    "fish-celebrity-list": "语音合成",
    "fish-celebrity-top10": "语音合成",
    "mimo-v2.5-tts": "语音合成",
    "mimo-v2.5-tts-voiceclone": "声音克隆",
    "mimo-v2.5-tts-voicedesign": "语音合成",
    "stepfun-tts": "语音合成",
    "stepfun-asr": "语音识别",
    "stepfun-rag": "AI平台工具",
    "stepfun-chat": "AI平台工具",
    "stepfun-image": "AI图像生成",
    "stepfun-search": "AI平台工具",
    "stepfun-realtime": "语音处理",
    "qianwen-audio-tts": "语音合成",
    "qianwen-text": "AI文本生成",
    "qianwen-vision": "多模态分析",
    "qianwen-model-selector": "AI平台工具",
    "qianwen-ops-auth": "AI平台工具",
    "qianwen-usage": "AI平台工具",
    "qianwen-update-check": "AI平台工具",
    "qianwen-ai-setup": "AI平台工具",
    "cf-model-catalog": "AI平台工具",
    "cf-text-generation": "AI文本生成",
    "cf-speech-to-text": "语音识别",
    "aliyun-bailian-maas-tts": "语音合成",
    "dashscope-private-tts": "语音合成",
    "llm-provider-management": "AI平台工具",
    "z-ai": "AI平台工具",
    "huggingface-hub": "MLOps",
    "llama-cpp": "MLOps",
    "serving-llms-vllm": "MLOps",
    "doubao-websearch": "搜索与信息获取",
    "anysearch": "搜索与信息获取",
    "web-search-extract": "搜索与信息获取",
    "firecrawl": "搜索与信息获取",
    "firecrawl-scrape": "搜索与信息获取",
    "firecrawl-search": "搜索与信息获取",
    "firecrawl-map": "搜索与信息获取",
    "firecrawl-agent": "搜索与信息获取",
    "agent-reach": "搜索与信息获取",
    "huashu-info-search": "搜索与信息获取",
    "sn-search-academic": "学术搜索",
    "sn-deep-research": "深度研究",
    "sn-research-report": "研究报告",
    "github-trending": "GitHub趋势",
    "github-ai-tool-scout": "GitHub工具发现",
    "claude-code": "AI编程",
    "codebuddy": "AI编程",
    "codex": "AI编程",
    "opencode": "AI编程",
    "autonomous-ai-agents": "AI Agent编排",
    "dispatching-parallel-agents": "AI Agent编排",
    "delegate_task_workflow": "AI Agent编排",
    "huashu-agent-swarm": "AI Agent编排",
    "executing-plans": "项目管理",
    "writing-plans": "项目管理",
    "plan": "项目管理",
    "finishing-a-development-branch": "开发流程",
    "receiving-code-review": "开发流程",
    "requesting-code-review": "开发流程",
    "simplify-code": "代码优化",
    "systematic-debugging": "调试",
    "test-driven-development": "测试",
    "subagent-driven-development": "AI Agent编排",
    "spike": "原型开发",
    "adapt-skill-to-hermes": "Skill开发",
    "hermes-agent-skill-authoring": "Skill开发",
    "persona-skill-authoring": "Skill开发",
    "skill-converter": "Skill开发",
    "writing-skills": "Skill开发",
    "third-party-skill-investigation": "工具评估",
    "image-to-code": "前端开发",
    "design-taste-frontend": "前端设计",
    "gpt-taste": "前端设计",
    "claude-design": "前端设计",
    "baoyu-design": "设计与UI",
    "industrial-brutalist-ui": "前端设计",
    "minimalist-ui": "前端设计",
    "high-end-visual-design": "前端设计",
    "archify": "架构图",
    "graphify": "知识图谱/项目管理",
    "excalidraw": "图表与架构图",
    "architecture-diagram": "图表与架构图",
    "fireworks-tech-graph": "图表与架构图",
    "baoyu-diagram": "图表与架构图",
    "baoyu-infographic": "信息图",
    "sn-infographic": "信息图",
    "canghe-infographic": "信息图",
    "infographic": "信息图",
    "data-visualization": "数据可视化",
    "flint-chart": "数据可视化",
    "sn-da-excel-workflow": "Excel数据分析",
    "amap-maps": "地图服务",
    "tencent-map": "地图服务",
    "didi-ride": "出行服务",
    "flyai-fliggy": "旅行服务",
    "ima-skill": "IMA知识库",
    "note-taking": "笔记管理",
    "obsidian": "笔记管理",
    "notion": "笔记管理",
    "yixiaoer": "多平台分发",
    "guizang-ppt-skill": "幻灯片",
    "guizang-social-card-skill": "社媒卡片",
    "baoku-cli": "知识库/PPT",
    "tencent-docs": "腾讯文档",
    "wjx-survey": "问卷星",
    "google-workspace": "Google服务",
    "email-and-himalaya": "邮件",
    "wechat-article-extract": "公众号工具",
    "wechat-history-crawler": "公众号工具",
    "baoyu-url-to-markdown": "文档工具",
    "baoyu-post-to-wechat": "公众号发布",
    "weread": "微信读书",
    "youtube-content": "YouTube内容",
    "youtube-viral-topic": "YouTube分析",
    "x-viral-topic": "X/Twitter分析",
    "xurl": "X/Twitter工具",
    "baoyu-post-to-x": "X/Twitter发布",
    "cn-tts": "语音合成综述",
    "tts-tooling": "语音合成综述",
    "tts-voice-catalog": "语音合成综述",
    "groq-whisper": "语音识别",
    "audio-processing-workflow": "音频处理",
    "media-processing": "媒体处理",
    "gif-search": "GIF搜索",
    "spotify": "音乐",
    "book-to-webpage": "知识管理",
    "book2web": "知识管理",
    "cangjie-skill": "知识蒸馏",
    "notebooklm": "NotebookLM",
    "ocr-and-documents": "OCR与文档",
    "document-conversion": "文档转换",
    "repo2ima": "知识管理",
    "baidu-netdisk-workflow": "百度网盘",
    "yun-storage": "云存储",
    "cloud-storage": "云存储",
    "devops": "DevOps",
    "cloudbase": "云开发",
    "tencent-cloud": "腾讯云",
    "volcengine-ark": "火山引擎",
    "aliyun-oss-storage": "阿里云OSS",
    "self-hosted-web-service-deployment": "自托管服务",
    "free-model-router-deployment": "AI网关",
    "free-model-router-start": "AI网关",
    "api-connectivity-test": "AI网关",
    "api-key-management": "AI网关",
    "llm-provider-management": "AI网关",
    "service-to-mcp": "MCP服务",
    "china-app-mcp-skill": "MCP服务",
    "mcp-porter-cn-apps": "MCP服务",
    "native-mcp": "MCP协议",
    "app-skill-integration": "工具集成",
    "cn-apps-mcp": "中国应用集成",
    "hermes-backup": "备份恢复",
    "hermes-config-backup": "备份恢复",
    "hermes-venv-recovery": "环境恢复",
    "hermes-web-backends": "Hermes配置",
    "hermes-agent": "Hermes配置",
    "system-diagnosis": "系统诊断",
    "disk-cleanup": "系统运维",
    "headless-cli-auth": "认证与登录",
    "google-oauth-setup": "认证与登录",
    "cli-tools-setup": "CLI工具",
    "nano-pdf": "PDF工具",
    "powerpoint": "PPT工具",
    "ai-cli-tools": "AI CLI工具",
}


def parse_skill_metadata(skill_dir):
    """Parse SKILL.md frontmatter from a skill directory."""
    sk = {"name": skill_dir.name, "path": str(skill_dir)}
    
    # Read SKILL.md
    smd = skill_dir / "SKILL.md"
    if not smd.exists():
        # Try nested (category/skill/SKILL.md)
        nested = list(skill_dir.rglob("SKILL.md"))
        if nested:
            smd = nested[0]
        else:
            sk["error"] = "No SKILL.md found"
            return sk
    
    try:
        text = smd.read_text(encoding="utf-8", errors="replace")
    except:
        sk["error"] = "Cannot read"
        return sk
    
    # Parse YAML frontmatter
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if m:
        front = m.group(1)
        for line in front.split('\n'):
            if ':' in line:
                key, _, val = line.partition(':')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == 'name':
                    sk['skill_name'] = val
                elif key == 'description':
                    sk['description'] = val
                elif key == 'tags':
                    sk['tags'] = [t.strip().strip('"').strip("'").strip('[]') for t in val.strip('[]').split(',')] if val else []
    
    sk.setdefault('description', '')
    sk.setdefault('tags', [])
    
    # Count words and lines
    body = text.split('---', 2)[-1] if m else text
    sk['body_words'] = len(body.split())
    sk['body_lines'] = len(body.split('\n'))
    
    return sk


def main():
    skills = []
    categories = defaultdict(list)
    tag_counter = Counter()
    
    # Find all skill directories: top-level + nested under umbrella dirs
    skill_dirs = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        # Check if this dir has its own SKILL.md (top-level skill)
        if (d / "SKILL.md").exists():
            skill_dirs.append(d)
        else:
            # Umbrella dir: find nested skill subdirs
            nested = list(d.rglob("SKILL.md"))
            for smd in nested:
                skill_dirs.append(smd.parent)
    
    for d in sorted(skill_dirs, key=lambda x: str(x)):
        meta = parse_skill_metadata(d)
        skills.append(meta)
        
        # Assign category
        cat = CATEGORY_MAP.get(meta['name'], '未分类')
        categories[cat].append(meta['name'])
        
        for t in meta.get('tags', []):
            if t:
                tag_counter[t] += 1
    
    # Build JSON report
    report = {
        "total_skills": len(skills),
        "categories": {cat: sorted(names) for cat, names in sorted(categories.items())},
        "category_counts": {cat: len(names) for cat, names in sorted(categories.items())},
        "top_tags": tag_counter.most_common(30),
        "skills": [{"name": s["name"], "description": s.get("description", ""), "category": CATEGORY_MAP.get(s['name'], '未分类'), "body_words": s.get('body_words', 0)} for s in skills],
    }
    
    # Write output
    (OUT_DIR / "skills_analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    
    # Also generate a graph-compatible JSON
    nodes = []
    edges = []
    
    # One node per skill
    seen = set()
    for s in skills:
        n = s['name']
        cat = CATEGORY_MAP.get(n, '未分类')
        if n not in seen:
            nd = {
                "id": n,
                "type": "skill",
                "category": cat,
                "description": s.get('description', '')[:100],
                "words": s.get('body_words', 0),
            }
            nodes.append(nd)
            seen.add(n)
    
    # Add category nodes
    cat_seen = set()
    for s in skills:
        cat = CATEGORY_MAP.get(s['name'], '未分类')
        if cat not in cat_seen:
            nodes.append({"id": f"cat:{cat}", "type": "category", "name": cat})
            cat_seen.add(cat)
        edges.append({"source": s['name'], "target": f"cat:{cat}", "relation": "belongs_to"})
    
    # Cross-reference: skills that share tags
    tag_to_skills = defaultdict(set)
    for s in skills:
        for t in s.get('tags', []):
            if t:
                tag_to_skills[t].add(s['name'])
    
    for tag, sks in tag_to_skills.items():
        sks_list = list(sks)
        for i in range(len(sks_list)):
            for j in range(i+1, len(sks_list)):
                edges.append({"source": sks_list[i], "target": sks_list[j], "relation": f"shared_tag:{tag}"})
    
    graph = {"nodes": nodes, "edges": edges[:5000]}  # cap edges
    (OUT_DIR / "skills_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2))
    
    # Print summary
    print(f"=== Hermes Skills 全面分析 ===")
    print(f"\n总计: {len(skills)} 个 Skills")
    print(f"\n分类统计 ({len(categories)} 个分类):")
    print("-" * 50)
    for cat, names in sorted(categories.items(), key=lambda x: -len(x[1])):
        bar = "█" * min(len(names), 30)
        print(f"  {bar} {cat}: {len(names)}个")
    
    print(f"\n热门标签 TOP 20:")
    print("-" * 50)
    for tag, cnt in tag_counter.most_common(20):
        print(f"  #{tag}: {cnt}个")
    
    print(f"\n各分类详情:")
    print("=" * 60)
    for cat, names in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"\n📁 {cat} ({len(names)}个):")
        for n in names:
            meta = next((s for s in skills if s['name'] == n), None)
            desc = (meta.get('description', '') or '')[:60]
            print(f"    • {n}")
            if desc:
                print(f"      {desc}")
    
    # Save report as HTML
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Hermes Skills 知识图谱</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f0f1a; color: #e0e0e0; padding: 2rem; }
h1 { font-size: 2rem; color: #8b5cf6; margin-bottom: 0.5rem; }
h2 { font-size: 1.3rem; color: #a78bfa; margin: 2rem 0 1rem; border-bottom: 1px solid #1e1e3a; padding-bottom: 0.5rem; }
.summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
.stat { background: #1a1a2e; border-radius: 12px; padding: 1.2rem; text-align: center; }
.stat .num { font-size: 2rem; font-weight: bold; color: #8b5cf6; }
.stat .label { font-size: 0.85rem; color: #888; margin-top: 0.3rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; margin: 1rem 0; }
.card { background: #1a1a2e; border-radius: 10px; padding: 1rem; border: 1px solid #2a2a4a; }
.card h3 { color: #c4b5fd; font-size: 0.95rem; margin-bottom: 0.3rem; }
.card .count { color: #8b5cf6; font-weight: bold; font-size: 0.85rem; }
.card .skills { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.5rem; }
.tag { background: #2a2a4a; color: #a78bfa; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
</style></head><body>
<h1>𖤍 Hermes Skills 知识图谱</h1>
<p style="color:#888;margin-bottom:1rem;">全面分析 · """ + str(len(skills)) + """ 个技能</p>
<div class="summary">
  <div class="stat"><div class="num">""" + str(len(skills)) + """</div><div class="label">Skills 总数</div></div>
  <div class="stat"><div class="num">""" + str(len(categories)) + """</div><div class="label">分类数</div></div>
  <div class="stat"><div class="num">""" + str(len(tag_counter)) + """</div><div class="label">标签数</div></div>
</div>
"""
    for cat, names in sorted(categories.items(), key=lambda x: -len(x[1])):
        bar = "█" * min(len(names), 25)
        size = "small" if len(names) <= 3 else ("medium" if len(names) <= 8 else "large")
        html += f'<div class="card"><h3>{cat}</h3><div class="count">{bar} {len(names)}个</div><div class="skills">'
        for n in names:
            html += f'<span class="tag">{n}</span>'
        html += '</div></div>'
    
    html += "</body></html>"
    (OUT_DIR / "skills_report.html").write_text(html, encoding="utf-8")
    
    print(f"\n\n报告已保存到: {OUT_DIR}/")
    print(f"  - skills_analysis.json (完整数据分析)")
    print(f"  - skills_graph.json (知识图谱数据)")
    print(f"  - skills_report.html (可视化报告)")

if __name__ == "__main__":
    main()
