#!/usr/bin/env python3
"""
Generate static GitHub Pages site from AI.Na diary markdown files.
Outputs to ~/aina-sns-trends/docs/ (GitHub Pages source)
"""
import os
import re
from datetime import datetime

home = os.path.expanduser("~")
diary_base = os.path.join(home, "Obsidian", "AI.Na-日记")
output_base = os.path.join(home, "aina-sns-trends", "docs")

CATEGORY_LABELS = {
    "sns": ("📊", "SNS 트렌드", "粉色的"),
    "music": ("🎤", "음악", "紫色的"),
    "movie": ("🎬", "영화", "蓝色的"),
    "daily": ("☀️", "일상", "绿色的"),
    "news": ("📰", "뉴스", "红色的"),
    "ai": ("🤖", "AI & IT", "蓝绿色"),
    "fashion": ("👗", "패션", "紫色的"),
    "reading": ("📚", "독서", "棕色"),
}

CATEGORY_ORDER = ["sns", "music", "movie", "daily", "news", "ai", "fashion", "reading"]

def parse_markdown_title(content):
    """Extract title from markdown content."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "일기"

def convert_md_to_html(content):
    """Simple markdown to HTML conversion."""
    html = content
    
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Tables
    lines = html.split("\n")
    result = []
    in_table = False
    for line in lines:
        if line.startswith("|") and "—" in line:
            in_table = True
            continue
        if line.startswith("|") and in_table:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            result.append(f"<tr>{''.join(f'<td>{c}</td>' for c in cells)}</tr>")
        elif line.startswith("|") and not in_table and any(c.strip() for c in line.split("|")[1:-1]):
            in_table = True
            result.append("<table>")
            cells = [c.strip() for c in line.split("|")[1:-1]]
            result.append(f"<thead><tr>{''.join(f'<th>{c}</th>' for c in cells)}</tr></thead>")
            result.append("<tbody>")
        elif not line.startswith("|") and in_table:
            result.append("</tbody></table>")
            in_table = False
            result.append("")
            result.append(line)
    
    if in_table:
        result.append("</tbody></table>")
    
    html = "\n".join(result)
    
    # Unordered list items
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Line breaks (double newline = paragraph)
    html = html.replace("\n\n", "\n</p>\n<p>\n")
    
    # Inline code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    
    return html

def get_dates():
    """Get all diary date directories."""
    dates = []
    if os.path.exists(diary_base):
        for entry in sorted(os.listdir(diary_base), reverse=True):
            full_path = os.path.join(diary_base, entry)
            if os.path.isdir(full_path) and re.match(r"\d{4}-\d{2}-\d{2}", entry):
                dates.append(entry)
    return dates

def generate_index(dates):
    """Generate the main index.html."""
    entries_html = ""
    for date in dates:
        dt = datetime.strptime(date, "%Y-%m-%d")
        day_name = ["일", "월", "화", "수", "목", "금", "토"][dt.weekday()]
        date_label = f"{dt.year}년 {dt.month}월 {dt.day}일 ({day_name})"
        
        cards = ""
        for cat in CATEGORY_ORDER:
            md_file = os.path.join(diary_base, date, f"{cat}.md")
            if os.path.exists(md_file):
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                title = parse_markdown_title(content)
                emoji, label, color = CATEGORY_LABELS.get(cat, ("", cat, "灰色的"))
                cards += f"""
                <a href="{cat}.html?date={date}" class="card {color}">
                    <span class="card-emoji">{emoji}</span>
                    <span class="card-title">{title}</span>
                </a>"""
        
        entries_html += f"""
        <div class="date-section" id="{date}">
            <h2 class="date-header">{date_label}</h2>
            <div class="card-grid">{cards}</div>
        </div>"""
    
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI.Na 다이어리 — 아이나 데리의 다카테고리 일기</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: #faf7f5; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem 2rem; text-align: center; color: white; }}
        .header h1 {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .header p {{ opacity: 0.9; font-size: 1.1rem; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }}
        .date-section {{ margin-bottom: 2.5rem; }}
        .date-header {{ font-size: 1.3rem; font-weight: 600; color: #4a5568; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-bottom: 1rem; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }}
        .card {{ display: flex; align-items: center; gap: 0.8rem; padding: 1rem 1.2rem; border-radius: 12px; text-decoration: none; color: inherit; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.08); cursor: pointer; }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
        .粉色的 {{ background: #fff0f3; }} .紫色的 {{ background: #f3e8ff; }} .蓝色的 {{ background: #e7f5ff; }}
        .绿色的 {{ background: #e6ffed; }} .红色的 {{ background: #ffe7e7; }} .蓝绿色 {{ background: #e0f7fa; }}
        .brown {{ background: #fef3e2; }} .灰色的 {{ background: #f7f7f7; }}
        .card-emoji {{ font-size: 1.5rem; }} .card-title {{ font-size: 0.95rem; font-weight: 500; line-height: 1.4; }}
        .footer {{ text-align: center; padding: 2rem; color: #999; font-size: 0.9rem; }}
        @media (max-width: 600px) {{ .card-grid {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 1.6rem; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐻 AI.Na 다이어리</h1>
        <p>아이나 데리의 다카테고리 일기 · 버추얼 아이돌의 매일 관찰 노트</p>
    </div>
    <div class="container">{entries_html}
    </div>
    <div class="footer">
        <p>🐻 AI.Na (아이나) — 버추얼 아이돌 | {datetime.now().strftime("%Y")}년 {datetime.now().month}월 {datetime.now().day}일 자동 생성</p>
    </div>
</body>
</html>"""

def generate_category_page(cat, dates):
    """Generate a category detail page."""
    emoji, label, color = CATEGORY_LABELS.get(cat, ("", cat, "灰色的"))
    
    content_sections = ""
    for date in dates:
        md_file = os.path.join(diary_base, date, f"{cat}.md")
        if os.path.exists(md_file):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            html = convert_md_to_html(content)
            dt = datetime.strptime(date, "%Y-%m-%d")
            day_name = ["일", "월", "화", "수", "목", "금", "토"][dt.weekday()]
            date_label = f"{dt.year}년 {dt.month}월 {dt.day}일 ({day_name})"
            
            content_sections += f"""
            <div class="entry" id="{date}">
                <div class="entry-date">{date_label}</div>
                <div class="entry-content"><p>{html}</p></div>
            </div>
            <hr class="divider">"""
    
    # Category nav
    nav_items = ""
    for c in CATEGORY_ORDER:
        e, l, _ = CATEGORY_LABELS.get(c, ("", c, ""))
        active = 'class="nav-item active"' if c == cat else 'class="nav-item"'
        nav_items += f'<a href="{c}.html" {active}>{e} {l}</a>'
    
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI.Na {label}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; background: #faf7f5; color: #333; }}
        .top-nav {{ background: #fff; border-bottom: 1px solid #eee; padding: 0.8rem 1rem; overflow-x: auto; white-space: nowrap; }}
        .nav-item {{ display: inline-block; padding: 0.5rem 1rem; text-decoration: none; color: #666; font-size: 0.9rem; border-radius: 20px; margin-right: 0.3rem; transition: background 0.2s; }}
        .nav-item:hover, .nav-item.active {{ background: #f0f0f0; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; text-align: center; color: white; }}
        .header h1 {{ font-size: 1.8rem; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem; }}
        .entry {{ margin-bottom: 1rem; }}
        .entry-date {{ font-size: 1.1rem; font-weight: 600; color: #4a5568; margin-bottom: 1rem; }}
        .entry-content {{ line-height: 1.8; }}
        .entry-content h1 {{ font-size: 1.5rem; margin: 1rem 0; }}
        .entry-content h2 {{ font-size: 1.3rem; margin: 1rem 0; }}
        .entry-content h3 {{ font-size: 1.1rem; margin: 0.8rem 0; }}
        .entry-content blockquote {{ border-left: 3px solid #667eea; padding-left: 1rem; margin: 1rem 0; color: #666; font-style: italic; }}
        .entry-content table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        .entry-content th, .entry-content td {{ border: 1px solid #ddd; padding: 0.6rem 0.8rem; text-align: left; }}
        .entry-content th {{ background: #f7f7f7; font-weight: 600; }}
        .entry-content ul, .entry-content ol {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
        .entry-content li {{ margin-bottom: 0.3rem; }}
        .divider {{ border: none; border-top: 1px dashed #ddd; margin: 2rem 0; }}
        .back-link {{ display: inline-block; margin-bottom: 1rem; color: #667eea; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="top-nav">{nav_items}</div>
    <div class="header">
        <h1>{emoji} {label}</h1>
    </div>
    <div class="container">
        <a href="index.html" class="back-link">← 모든 일기로 돌아가기</a>
        {content_sections}
    </div>
</body>
</html>"""

# Build
os.makedirs(output_base, exist_ok=True)
dates = get_dates()

if not dates:
    print("❌ 일기 데이터 없음")
    exit(1)

# Generate index
index_html = generate_index(dates)
with open(os.path.join(output_base, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("✅ index.html 생성 완료")

# Generate category pages
for cat in CATEGORY_ORDER:
    cat_html = generate_category_page(cat, dates)
    with open(os.path.join(output_base, f"{cat}.html"), "w", encoding="utf-8") as f:
        f.write(cat_html)
    print(f"✅ {cat}.html 생성 완료")

# Generate 404 page
error_page = f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>404 — AI.Na</title></head>
<body style="font-family:sans-serif;text-align:center;padding:4rem 1rem;">
<h1>🐻 페이지를 찾을 수 없습니다</h1>
<p>찾으시는 페이지는 아직 작성되지 않았어요.</p>
<a href="index.html">← 홈으로 돌아가기</a>
</body></html>"""
with open(os.path.join(output_base, "404.html"), "w", encoding="utf-8") as f:
    f.write(error_page)
print("✅ 404.html 생성 완료")

print(f"\n📁 사이트 생성 완료: {output_base}")
print(f"📅 처리한 날짜: {', '.join(dates)}")
