#!/usr/bin/env python3
"""
Generate a clean static documentation site for awesome-ai4bio-skills.
Each skill gets its own HTML page. Index page lists all skills.
Style: clean ReadTheDocs-like, inspired by esm skill docs.
"""

import re
import os
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path(__file__).parent / "skills"
OUTPUT_DIR = Path(__file__).parent / "site"
TEMPLATE_DIR = Path(__file__).parent / "templates"

# ─── Category mapping ───────────────────────────────────────────────────────

CATEGORIES = {
    "Sequence & Genomics": [
        "pysam", "biopython", "scikit-bio", "gget", "gtars",
        "bioservices", "deeptools", "polars-bio", "dask",
        "zarr-python", "tiledbvcf", "polars",
    ],
    "Single-Cell & Multi-Omics": [
        "scanpy", "scvi-tools", "anndata", "scvelo", "cellxgene-census",
        "arboreto", "lamindb", "geniml", "pydeseq2", "hypogenic", "primekg",
    ],
    "Protein & Structure": [
        "esm", "rdkit", "deepchem", "torchdrug", "diffdock", "datamol",
        "molfeat", "medchem", "pytdc", "pymatgen", "cobrapy",
        "molecular-dynamics", "glycoengineering", "adaptyv", "etetoolkit",
    ],
    "Mass Spectrometry & Metabolism": [
        "matchms", "pyopenms",
    ],
    "Literature & Databases": [
        "database-lookup", "paper-lookup",
    ],
    "Visualization & Analysis": [
        "scientific-visualization", "exploratory-data-analysis",
        "networkx", "matplotlib", "seaborn",
    ],
}

ALL_SKILLS = {s for cats in CATEGORIES.values() for s in cats}

# ─── Markdown → HTML renderer (lightweight, no external deps) ─────────────────

def markdown_to_html(text: str) -> str:
    """Convert markdown to HTML with code highlighting support."""
    lines = text.split("\n")
    html_lines = []
    in_code = False
    code_block_lang = ""
    code_buffer = []

    for line in lines:
        # Fenced code blocks
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_block_lang = line[3:].strip()
                code_buffer = []
            else:
                in_code = False
                lang_class = f' class="language-{code_block_lang}"' if code_block_lang else ""
                escaped = "\n".join(code_buffer).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_lines.append(f'<pre><code{lang_class}>{escaped}</code></pre>')
                code_block_lang = ""
                code_buffer = []
            continue

        if in_code:
            code_buffer.append(line)
            continue

        # Headers
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            html_lines.append(f'<h{level}>{inline_format(m.group(2))}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r'^---+$', line):
            html_lines.append("<hr>")
            continue

        # Unordered list
        if re.match(r'^[\-\*]\s+', line):
            html_lines.append(f'<li>{inline_format(line[2:])}</li>')
            continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            html_lines.append(f'<li>{inline_format(m.group(1))}</li>')
            continue

        # Blockquote
        m = re.match(r'^>\s?(.*)', line)
        if m:
            html_lines.append(f'<blockquote>{inline_format(m.group(1))}</blockquote>')
            continue

        # Table — detect and collect rows
        if "|" in line and line.strip().startswith("|"):
            html_lines.append(f'<p>{inline_format(line)}</p>')
            continue

        # Empty line
        if not line.strip():
            html_lines.append("")
            continue

        # Paragraph
        html_lines.append(f'<p>{inline_format(line)}</p>')

    # Wrap consecutive <li> in <ul>
    result = "\n".join(html_lines)
    result = re.sub(r'(<li>.*?</li>\n?)+', lambda m: "<ul>" + m.group() + "</ul>", result)

    return result


def inline_format(text: str) -> str:
    """Apply inline formatting (bold, italic, code, links)."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


def get_skill_meta(skill_dir: Path) -> dict:
    """Extract name and description from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"name": skill_dir.name, "description": ""}

    content = skill_md.read_text()
    name = skill_dir.name
    description = ""

    # Extract from first heading or first paragraph
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        name = m.group(1).strip()

    # Try frontmatter description
    fm_match = re.search(r'description:\s*(.+?)(?:\n|--$)', content, re.DOTALL)
    if fm_match:
        description = fm_match.group(1).strip()

    # Fallback: first non-empty non-header line
    if not description:
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                description = line
                break

    return {"name": name, "description": description[:200]}


def get_references(skill_dir: Path) -> list:
    """List reference files in the references/ subdirectory."""
    ref_dir = skill_dir / "references"
    if not ref_dir.exists():
        return []
    refs = []
    for f in sorted(ref_dir.iterdir()):
        if f.suffix == ".md":
            refs.append({
                "name": f.stem.replace("-", " ").replace("_", " ").title(),
                "file": f.name,
                "content": markdown_to_html(f.read_text()),
            })
    return refs


def get_skill_content(skill_dir: Path) -> str:
    """Render SKILL.md content without the frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "<p>No documentation available.</p>"

    content = skill_md.read_text()

    # Strip frontmatter
    if content.startswith("---"):
        end = content.find("\n---", 4)
        if end != -1:
            content = content[end+4:]

    # Strip YAML frontmatter blocks
    content = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)

    return markdown_to_html(content.strip())


# ─── HTML templates ─────────────────────────────────────────────────────────

CSS = """
:root {
  --bg: #fafbfc;
  --sidebar-bg: #1e2530;
  --sidebar-text: #c9d1d9;
  --sidebar-hover: #2d3748;
  --accent: #0969da;
  --accent-light: #dbeafe;
  --text: #24292f;
  --text-muted: #57606a;
  --border: #d0d7de;
  --code-bg: #f6f8fa;
  --header-bg: #ffffff;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  display: flex;
  min-height: 100vh;
}
#sidebar {
  width: 260px;
  min-width: 260px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  position: fixed;
  top: 0; left: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 24px 0;
}
#sidebar .logo {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 12px;
  letter-spacing: 0.3px;
}
#sidebar .logo span { color: #58a6ff; }
#sidebar .section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #8b949e;
  padding: 16px 20px 6px;
}
#sidebar a {
  display: block;
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 13.5px;
  padding: 5px 20px;
  border-radius: 0;
  transition: background 0.15s, color 0.15s;
}
#sidebar a:hover { background: var(--sidebar-hover); color: #fff; }
#sidebar a.active { background: var(--accent); color: #fff; }
#main {
  margin-left: 260px;
  flex: 1;
  min-width: 0;
}
#topbar {
  background: var(--header-bg);
  border-bottom: 1px solid var(--border);
  padding: 0 40px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
}
#topbar .breadcrumb {
  font-size: 14px;
  color: var(--text-muted);
}
#topbar .breadcrumb a { color: var(--accent); text-decoration: none; }
#topbar .breadcrumb a:hover { text-decoration: underline; }
#topbar .actions a {
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  margin-left: 16px;
}
#topbar .actions a:hover { color: var(--accent); }
#content {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 40px 80px;
}
#content h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
#content .description {
  font-size: 16px;
  color: var(--text-muted);
  margin-bottom: 32px;
}
#content h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 36px 0 14px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
#content h3 { font-size: 16px; font-weight: 600; margin: 24px 0 10px; }
#content h4 { font-size: 14px; font-weight: 600; margin: 20px 0 8px; }
#content p { margin: 0 0 14px; }
#content ul, #content ol { margin: 0 0 14px 24px; }
#content li { margin-bottom: 6px; }
#content a { color: var(--accent); text-decoration: none; }
#content a:hover { text-decoration: underline; }
#content code {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 13px;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}
#content pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 0 0 20px;
}
#content pre code {
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  line-height: 1.6;
}
#content blockquote {
  border-left: 4px solid var(--accent);
  background: var(--accent-light);
  padding: 12px 16px;
  margin: 0 0 20px;
  border-radius: 0 6px 6px 0;
}
#content table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 20px;
  font-size: 14px;
}
#content th {
  background: var(--code-bg);
  text-align: left;
  padding: 8px 12px;
  border: 1px solid var(--border);
  font-weight: 600;
}
#content td {
  padding: 8px 12px;
  border: 1px solid var(--border);
}
#content tr:nth-child(even) td { background: var(--code-bg); }
#content hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
.ref-section {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 2px solid var(--border);
}
.ref-section h2 { font-size: 18px; margin-bottom: 16px; }
.ref-card {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 16px;
}
.ref-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 10px;
  color: var(--accent);
}
#footer {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
  border-top: 1px solid var(--border);
  background: var(--header-bg);
}
@media (max-width: 768px) {
  #sidebar { display: none; }
  #main { margin-left: 0; }
  #content { padding: 24px 20px 60px; }
}
"""

INDEX_CSS = """
.hero {
  background: linear-gradient(135deg, #1e2530 0%, #2d3748 100%);
  color: #fff;
  padding: 72px 40px;
  text-align: center;
}
.hero h1 { font-size: 36px; font-weight: 800; margin-bottom: 12px; }
.hero p { font-size: 18px; color: #8b949e; max-width: 600px; margin: 0 auto 24px; }
.hero .badges span {
  display: inline-block;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 13px;
  margin: 4px;
  color: #c9d1d9;
}
.categories { padding: 48px 40px; max-width: 1100px; margin: 0 auto; }
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 24px;
}
.cat-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}
.cat-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.cat-header {
  background: var(--sidebar-bg);
  color: #fff;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 600;
}
.cat-header span { color: #58a6ff; margin-right: 6px; }
.cat-items { padding: 8px 0; }
.cat-items a {
  display: flex;
  align-items: center;
  padding: 9px 20px;
  text-decoration: none;
  color: var(--text);
  font-size: 14px;
  transition: background 0.15s;
}
.cat-items a:hover { background: var(--accent-light); color: var(--accent); }
.cat-items .skill-name {
  font-weight: 600;
  min-width: 140px;
}
.cat-items .skill-desc {
  color: var(--text-muted);
  font-size: 12.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cat-items .skill-new {
  margin-left: auto;
  background: var(--accent);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
"""


def make_sidebar(active_skill: str = None) -> str:
    """Build sidebar HTML."""
    sections = []
    for cat_name, skills in CATEGORIES.items():
        sections.append(f'<div class="section-label">{cat_name}</div>')
        for s in sorted(skills):
            cls = "active" if s == active_skill else ""
            display = s.replace("-", " ").replace("_", " ").title()
            sections.append(f'<a href="{s}.html" class="{cls}">{display}</a>')
    return f"""
<nav id="sidebar">
  <div class="logo">🧬 <span>AI4Bio</span> Skills</div>
  <a href="index.html">🏠 Overview</a>
  {"".join(sections)}
</nav>
"""


def skill_page_html(skill_name: str, meta: dict, content: str, refs: list) -> str:
    """Generate a full skill page."""
    active_link = make_sidebar(skill_name)
    ref_cards = ""
    for ref in refs:
        ref_cards += f"""
<div class="ref-card">
  <h3>📄 {ref['name']}</h3>
  {ref['content']}
</div>"""
    refs_html = f'<div class="ref-section"><h2>Reference Documentation</h2>{ref_cards}</div>' if refs else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['name']} — AI4Bio Skills</title>
  <style>{CSS}</style>
</head>
<body>
{active_link}
<div id="main">
  <div id="topbar">
    <div class="breadcrumb"><a href="index.html">AI4Bio Skills</a> / {meta['name']}</div>
    <div class="actions"><a href="https://github.com/junior1p/awesome-ai4bio-skills">GitHub ↗</a></div>
  </div>
  <div id="content">
    <h1>{meta['name']}</h1>
    <p class="description">{meta['description']}</p>
    {content}
    {refs_html}
  </div>
  <div id="footer">
    awesome-ai4bio-skills · {datetime.now().year} · Built for the computational biology community
  </div>
</div>
</body>
</html>"""


def index_page_html(skills_meta: dict) -> str:
    """Generate the index/overview page."""
    cat_blocks = []
    for cat_name, cat_skills in CATEGORIES.items():
        items = []
        for s in sorted(cat_skills):
            meta = skills_meta.get(s, {"name": s, "description": ""})
            desc = meta.get("description", "")
            items.append(f"""
        <a href="{s}.html">
          <span class="skill-name">{meta['name']}</span>
          <span class="skill-desc">{desc[:80]}{'...' if len(desc)>80 else ''}</span>
        </a>""")
        cat_blocks.append(f"""
    <div class="cat-card">
      <div class="cat-header"><span>▸</span> {cat_name}</div>
      <div class="cat-items">{"".join(items)}</div>
    </div>""")

    total = sum(len(cats) for cats in CATEGORIES.values())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI4Bio Skills — Computational Biology Agent Skills</title>
  <style>
{CSS}
{CSS}
{CSS}
{CSS}
body {{ background: var(--bg); }}
{INDEX_CSS}
  </style>
</head>
<body>
{make_sidebar()}
<div id="main">
  <div id="topbar">
    <div class="breadcrumb">🧬 Computational Biology Skills</div>
    <div class="actions"><a href="https://github.com/junior1p/awesome-ai4bio-skills">GitHub ↗</a></div>
  </div>
  <div class="hero">
    <h1>AI4Bio Skills</h1>
    <p>Computational biology & bioinformatics skills for AI agents. Powered by the scientific-agent-skills ecosystem.</p>
    <div class="badges">
      <span>🧬 {total} Skills</span>
      <span>🧪 Multi-Omics</span>
      <span>💊 Drug Discovery</span>
      <span>🧗 Protein Design</span>
      <span>🔬 Genomics</span>
    </div>
  </div>
  <div class="categories">
    <div class="cat-grid">{"".join(cat_blocks)}</div>
  </div>
  <div id="footer">
    awesome-ai4bio-skills · {datetime.now().year} · Built for the computational biology community
  </div>
</div>
</body>
</html>"""


# ─── Main generator ─────────────────────────────────────────────────────────

def generate():
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "skills").mkdir(exist_ok=True)

    skills_meta = {}

    # Generate individual skill pages
    for skill_name in sorted(ALL_SKILLS):
        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.exists():
            print(f"⚠️  {skill_name}: directory not found, skipping")
            continue

        meta = get_skill_meta(skill_dir)
        skills_meta[skill_name] = meta

        content = get_skill_content(skill_dir)
        refs = get_references(skill_dir)
        html = skill_page_html(skill_name, meta, content, refs)

        out_path = OUTPUT_DIR / f"{skill_name}.html"
        out_path.write_text(html)
        print(f"✅ {skill_name} → {out_path.name}")

    # Generate index
    index_html = index_page_html(skills_meta)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"\n✅ index.html → {OUTPUT_DIR / 'index.html'}")

    # Copy a simple robots.txt
    (OUTPUT_DIR / "robots.txt").write_text("User-agent: *\nAllow: /\n")

    print(f"\n🎉 Site generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate()
