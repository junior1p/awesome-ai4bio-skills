#!/usr/bin/env python3
"""
Generate a beautiful static documentation site for awesome-ai4bio-skills.
Design system: ESM2-inspired with Instrument Serif, DM Sans, JetBrains Mono.
Color palette: Blue #1B6CA8, Green #2DAD7C, Orange #E88C30
"""

import re
import os
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path(__file__).parent / "skills"
OUTPUT_DIR = Path(__file__).parent  # writes to repo root
PREFIX = "/awesome-ai4bio-skills"  # URL prefix for all links

# ─── Category mapping ───────────────────────────────────────────────────────

CATEGORIES = {
    "🧬 Sequence & Genomics": [
        "pysam", "biopython", "scikit-bio", "gget", "gtars",
        "bioservices", "deeptools", "polars-bio", "dask",
        "zarr-python", "tiledbvcf", "polars",
    ],
    "🔬 Single-Cell & Multi-Omics": [
        "scanpy", "scvi-tools", "anndata", "scvelo", "cellxgene-census",
        "arboreto", "lamindb", "geniml", "pydeseq2", "hypogenic", "primekg",
    ],
    "💊 Protein & Structure": [
        "esm", "rdkit", "deepchem", "torchdrug", "diffdock", "datamol",
        "molfeat", "medchem", "pytdc", "pymatgen", "cobrapy",
        "molecular-dynamics", "glycoengineering", "adaptyv", "etetoolkit",
    ],
    "⚗️ Mass Spectrometry & Metabolism": [
        "matchms", "pyopenms",
    ],
    "📚 Literature & Databases": [
        "database-lookup", "paper-lookup",
    ],
    "📊 Visualization & Analysis": [
        "scientific-visualization", "exploratory-data-analysis",
        "networkx", "matplotlib", "seaborn",
    ],
}

ALL_SKILLS = {s for cats in CATEGORIES.values() for s in cats}
TOTAL_SKILLS = sum(len(cats) for cats in CATEGORIES.values())

# ─── Markdown → HTML renderer ───────────────────────────────────────────────

def markdown_to_html(text: str) -> str:
    lines = text.split("\n")
    html_lines = []
    in_code = False
    code_block_lang = ""
    code_buffer = []

    for line in lines:
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

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            # Skip h1 — title is rendered by the page template
            if level == 1:
                continue
            html_lines.append(f'<h{level}>{inline_format(m.group(2))}</h{level}>')
            continue

        if re.match(r'^---+$', line):
            html_lines.append("<hr>")
            continue

        if re.match(r'^[\-\*]\s+', line):
            html_lines.append(f'<li>{inline_format(line[2:])}</li>')
            continue

        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            html_lines.append(f'<li>{inline_format(m.group(1))}</li>')
            continue

        m = re.match(r'^>\s?(.*)', line)
        if m:
            html_lines.append(f'<blockquote>{inline_format(m.group(1))}</blockquote>')
            continue

        if "|" in line and line.strip().startswith("|"):
            html_lines.append(f'<p>{inline_format(line)}</p>')
            continue

        if not line.strip():
            html_lines.append("")
            continue

        html_lines.append(f'<p>{inline_format(line)}</p>')

    result = "\n".join(html_lines)
    result = re.sub(r'(<li>.*?</li>\n?)+', lambda m: "<ul>" + m.group() + "</ul>", result)
    return result


def inline_format(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', rf'<a href="{PREFIX}/\2">\1</a>', text)
    return text


def get_skill_meta(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"name": skill_dir.name, "description": ""}

    content = skill_md.read_text()
    name = skill_dir.name
    description = ""

    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        name = m.group(1).strip()

    fm_match = re.search(r'description:\s*(.+?)(?:\n|--$)', content, re.DOTALL)
    if fm_match:
        description = fm_match.group(1).strip()

    if not description:
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                description = line
                break

    return {"name": name, "description": description[:200]}


def get_references(skill_dir: Path) -> list:
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
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "<p>No documentation available.</p>"

    content = skill_md.read_text()
    if content.startswith("---"):
        end = content.find("\n---", 4)
        if end != -1:
            content = content[end+4:]
    content = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)
    return markdown_to_html(content.strip())

# ─── Design system (ESM2-inspired) ─────────────────────────────────────────

CSS = """
:root{
  --bg-deep:#F7F9FC;
  --bg-surface:#EEF2F8;
  --bg-card:#fff;
  --text-primary:#0F1923;
  --text-secondary:#4A5568;
  --text-dim:#94A3B8;
  --accent:#1B6CA8;
  --accent-bright:#0D4F8A;
  --accent-glow:rgba(27,108,168,.07);
  --accent-light:#D6E8F7;
  --accent-2:#2DAD7C;
  --accent-2-light:#D1F5E9;
  --accent-warn:#E88C30;
  --sidebar-bg:#161B22;
  --serif:'Instrument Serif',Georgia,serif;
  --sans:'DM Sans',-apple-system,sans-serif;
  --mono:'JetBrains Mono',monospace;
  --max-w:780px;
  --wide-w:1080px;
  --shadow-sm:0 1px 3px rgba(0,0,0,.04),0 1px 2px rgba(0,0,0,.03);
  --shadow-md:0 4px 16px rgba(27,108,168,.06),0 2px 6px rgba(0,0,0,.04);
  --shadow-lg:0 12px 40px rgba(27,108,168,.08),0 4px 12px rgba(0,0,0,.04);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:17px;scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{background:var(--bg-deep);color:var(--text-primary);font-family:var(--sans);line-height:1.72;font-weight:370;overflow-x:hidden}
::selection{background:#D6E8F7;color:#0D4F8A}
.scroll-progress{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(90deg,#1B6CA8,#2DAD7C,#E88C30,#1B6CA8);background-size:200% 100%;animation:shimmerBar 3s ease infinite;z-index:9999}
@keyframes shimmerBar{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:.8rem clamp(1.5rem,5vw,3rem);display:flex;align-items:center;justify-content:space-between;background:rgba(247,249,252,.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid rgba(27,108,168,.06);transition:all .3s}
nav .nav-brand{font-family:var(--mono);font-size:.8rem;font-weight:500;color:var(--accent);text-decoration:none;letter-spacing:.05em}
nav .nav-links{display:flex;gap:2rem;list-style:none}
nav .nav-links a{font-size:.82rem;color:var(--text-secondary);text-decoration:none;font-weight:400;transition:color .2s}
nav .nav-links a:hover{color:var(--accent)}
@media(max-width:600px){nav .nav-links{display:none}}

/* ── Page wrapper ── */
.page{min-height:100vh;padding-top:60px}

/* ── Hero ── */
.hero{position:relative;min-height:52vh;display:flex;flex-direction:column;justify-content:flex-end;padding:0 clamp(1.5rem,5vw,4rem) 4rem;overflow:hidden;background:#fff}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 75% 10%,rgba(27,108,168,.08) 0%,transparent 60%),radial-gradient(ellipse 50% 50% at 10% 80%,rgba(45,173,124,.08) 0%,transparent 55%),radial-gradient(ellipse 40% 40% at 90% 85%,rgba(232,140,48,.06) 0%,transparent 50%);z-index:0}
.hero-grid{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(27,108,168,.05) 1px,transparent 1px);background-size:32px 32px;mask-image:radial-gradient(ellipse 80% 70% at 50% 40%,black 10%,transparent 70%);-webkit-mask-image:radial-gradient(ellipse 80% 70% at 50% 40%,black 10%,transparent 70%);z-index:0}
.hero-content{position:relative;z-index:1;max-width:var(--wide-w);margin:0 auto;width:100%}
.hero-label{font-family:var(--mono);font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin-bottom:1.8rem;opacity:0;animation:fadeUp .8s ease-out .2s forwards}
.hero-title{font-family:var(--serif);font-size:clamp(2.8rem,6.5vw,5.5rem);line-height:1.06;font-weight:400;color:var(--text-primary);max-width:16ch;margin-bottom:1.8rem;opacity:0;animation:fadeUp .9s ease-out .35s forwards}
.hero-title em{font-style:italic;color:var(--accent)}
.hero-sub{font-size:1.05rem;color:var(--text-secondary);max-width:56ch;line-height:1.68;margin-bottom:2.5rem;opacity:0;animation:fadeUp .9s ease-out .5s forwards}
.hero-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1rem;max-width:560px;opacity:0;animation:fadeUp .9s ease-out .8s forwards;margin-top:1rem}
.stat-card{background:var(--bg-surface);border-radius:12px;padding:1rem 1.2rem;border:1px solid rgba(27,108,168,.07)}
.stat-card .stat-num{font-family:var(--serif);font-size:1.7rem;font-weight:400;color:var(--accent);line-height:1}
.stat-card .stat-num.green{color:var(--accent-2)}
.stat-card .stat-num.orange{color:var(--accent-warn)}
.stat-card .stat-label{font-size:.72rem;color:var(--text-dim);margin-top:.3rem;font-family:var(--mono);letter-spacing:.03em}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}

/* ── Content sections ── */
.content-section{padding:5rem clamp(1.5rem,5vw,4rem);max-width:var(--wide-w);margin:0 auto}
.section-label{font-family:var(--mono);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:1rem;opacity:.8}
.section-title{font-family:var(--serif);font-size:clamp(1.8rem,4vw,2.8rem);line-height:1.15;font-weight:400;margin-bottom:1.2rem}
.section-sub{font-size:1rem;color:var(--text-secondary);max-width:58ch;line-height:1.7;margin-bottom:2.5rem}

/* ── Category cards grid ── */
.cat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
.cat-card{background:var(--bg-card);border-radius:14px;overflow:hidden;border:1px solid rgba(27,108,168,.08);box-shadow:var(--shadow-sm);transition:transform .2s,box-shadow .2s}
.cat-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-md)}
.cat-header{padding:14px 20px;font-size:.78rem;font-weight:600;color:#fff;font-family:var(--mono);letter-spacing:.05em}
.cat-items a{display:flex;align-items:center;padding:10px 20px;text-decoration:none;color:var(--text-primary);font-size:.88rem;transition:background .15s}
.cat-items a:hover{background:var(--accent-light);color:var(--accent)}
.cat-items .skill-name{font-weight:500;min-width:120px}
.cat-items .skill-desc{color:var(--text-dim);font-size:.75rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-left:auto;padding-left:1rem}
.cat-items .skill-badge{margin-left:auto;padding-left:.5rem}
.cat-items .badge{font-family:var(--mono);font-size:.62rem;padding:2px 7px;border-radius:8px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.badge-blue{background:#D6E8F7;color:#0D4F8A}
.badge-green{background:#D1F5E9;color:#1A7A55}
.badge-orange{background:#FDEEDE;color:#B5601A}
.badge-purple{background:#EDE7F6;color:#5E35B1}
.badge-teal{background:#E0F2F1;color:#00695C}

/* ── Skill detail page ── */
.skill-layout{display:grid;grid-template-columns:260px 1fr;min-height:100vh}
@media(max-width:768px){.skill-layout{grid-template-columns:1fr}}
.sidebar{position:fixed;top:60px;left:0;width:260px;height:calc(100vh - 60px);overflow-y:auto;background:var(--sidebar-bg);border-right:1px solid rgba(27,108,168,.06);padding:24px 0}
@media(max-width:768px){.sidebar{display:none}}
.sidebar-logo{font-size:.82rem;font-weight:700;color:#fff;padding:0 20px 20px;margin-bottom:8px;font-family:var(--mono);letter-spacing:.05em}
.sidebar-logo span{color:#58a6ff}
.sidebar-section{font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:#8b949e;padding:14px 20px 6px;font-family:var(--mono)}
.sidebar a{display:block;color:#c9d1d9;text-decoration:none;font-size:.85rem;padding:5px 20px;transition:background .15s,color .15s}
.sidebar a:hover{background:rgba(27,108,168,.15);color:#fff}
.sidebar a.active{background:var(--accent);color:#fff}
.sidebar a .cat-icon{margin-right:6px}
.main-content{margin-left:260px;flex:1;min-width:0}
@media(max-width:768px){.main-content{margin-left:0}}
.topbar{background:rgba(247,249,252,.9);backdrop-filter:blur(12px);border-bottom:1px solid rgba(27,108,168,.06);padding:0 40px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:60px;z-index:10}
.breadcrumb{font-size:.82rem;color:var(--text-dim);font-family:var(--mono)}
.breadcrumb a{color:var(--accent);text-decoration:none}
.breadcrumb a:hover{text-decoration:underline}
.topbar-actions a{font-size:.78rem;color:var(--text-dim);text-decoration:none;margin-left:16px;font-family:var(--mono)}
.topbar-actions a:hover{color:var(--accent)}
.skill-content{padding:48px 40px 80px;max-width:860px}
.skill-content h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3.2rem);font-weight:400;margin-bottom:12px;padding-bottom:16px;border-bottom:1px solid rgba(27,108,168,.1)}
.skill-content .desc{font-size:1.05rem;color:var(--text-secondary);margin-bottom:2.5rem;line-height:1.7}
.skill-content h2{font-family:var(--serif);font-size:clamp(1.3rem,3vw,1.8rem);font-weight:400;margin:2.5rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid rgba(27,108,168,.08)}
.skill-content h3{font-size:.95rem;font-weight:600;margin:1.5rem 0 .6rem;color:var(--text-primary)}
.skill-content p{margin-bottom:14px;font-size:.95rem;color:var(--text-secondary);line-height:1.75}
.skill-content ul,.skill-content ol{margin:0 0 14px 24px}
.skill-content li{margin-bottom:6px;font-size:.9rem;color:var(--text-secondary)}
.skill-content a{color:var(--accent);text-decoration:none}
.skill-content a:hover{text-decoration:underline}
.skill-content code{background:var(--bg-surface);border:1px solid rgba(27,108,168,.08);border-radius:4px;padding:1px 5px;font-size:.8rem;font-family:var(--mono)}
.skill-content pre{background:var(--bg-surface);border:1px solid rgba(27,108,168,.08);border-radius:10px;padding:20px;overflow-x:auto;margin:0 0 24px}
.skill-content pre code{background:none;border:none;padding:0;font-size:.82rem;line-height:1.65}
.skill-content blockquote{border-left:3px solid var(--accent-2);background:var(--accent-2-light);padding:14px 18px;border-radius:0 10px 10px 0;margin:0 0 20px}
.skill-content blockquote p{color:var(--text-primary);margin:0}
.skill-content table{width:100%;border-collapse:collapse;margin:0 0 20px;font-size:.85rem}
.skill-content th{background:var(--bg-surface);text-align:left;padding:10px 14px;border:1px solid rgba(27,108,168,.08);font-weight:600;color:var(--accent);font-family:var(--mono);font-size:.72rem;letter-spacing:.05em;text-transform:uppercase}
.skill-content td{padding:9px 14px;border:1px solid rgba(27,108,168,.08)}
.skill-content tr:nth-child(even) td{background:var(--bg-surface)}
.skill-content hr{border:none;border-top:1px solid rgba(27,108,168,.08);margin:2.5rem 0}

/* Reference cards */
.ref-section{margin-top:3rem;padding-top:2rem;border-top:2px solid rgba(27,108,168,.08)}
.ref-section-title{font-family:var(--mono);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:1.2rem}
.ref-card{background:var(--bg-card);border-radius:12px;padding:1.2rem 1.5rem;border:1px solid rgba(27,108,168,.08);box-shadow:var(--shadow-sm);margin-bottom:1rem}
.ref-card h3{font-size:.88rem;font-weight:600;color:var(--accent);margin-bottom:.6rem;font-family:var(--sans)}
.ref-card p{font-size:.82rem;color:var(--text-secondary);line-height:1.65;margin:0}

/* ── Footer ── */
footer{padding:2rem clamp(1.5rem,5vw,3rem);text-align:center;color:var(--text-dim);font-size:.75rem;font-family:var(--mono);border-top:1px solid rgba(27,108,168,.06)}
footer a{color:var(--accent);text-decoration:none}
footer a:hover{text-decoration:underline}
"""

# Badge colors per category
CAT_COLORS = {
    "🧬 Sequence & Genomics": "blue",
    "🔬 Single-Cell & Multi-Omics": "purple",
    "💊 Protein & Structure": "green",
    "⚗️ Mass Spectrometry & Metabolism": "orange",
    "📚 Literature & Databases": "teal",
    "📊 Visualization & Analysis": "blue",
}

def make_nav(active_skill=None):
    links = f'<a href="{PREFIX}/" class="nav-brand">🧬 AI4Bio Skills</a>'
    links += '<ul class="nav-links">'
    links += f'<li><a href="{PREFIX}/">Overview</a></li>'
    links += '<li><a href="https://github.com/junior1p/awesome-ai4bio-skills" target="_blank">GitHub</a></li>'
    links += '</ul>'
    return f'<nav>{links}</nav>'


def make_sidebar(active_skill=None):
    sections = []
    for cat_name, skills in CATEGORIES.items():
        icon = cat_name.split()[0]
        sections.append(f'<div class="sidebar-section">{icon} {cat_name.split(" ",1)[1]}</div>')
        for s in sorted(skills):
            cls = "active" if s == active_skill else ""
            display = s.replace("-", " ").replace("_", " ").title()
            sections.append(f'<a href="{PREFIX}/{s}.html" class="{cls}">{display}</a>')
    return f"""
<div class="sidebar">
  <div class="sidebar-logo">🧬 <span>AI4Bio</span> Skills</div>
  <a href="{PREFIX}/" style="font-size:.8rem;color:#58a6ff;text-decoration:none;padding:4px 20px 12px;display:block">← All Skills</a>
  {"".join(sections)}
</div>"""


def skill_page_html(skill_name: str, meta: dict, content: str, refs: list) -> str:
    ref_cards = ""
    for ref in refs:
        ref_cards += f"""
<div class="ref-card">
  <h3>📄 {ref['name']}</h3>
  {ref['content']}
</div>"""
    refs_html = f'<div class="ref-section"><div class="ref-section-title">Reference Documentation</div>{ref_cards}</div>' if refs else ""

    badge_color = "blue"
    for cat, skills in CATEGORIES.items():
        if skill_name in skills:
            badge_color = CAT_COLORS.get(cat, "blue")
            break

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['name']} — AI4Bio Skills</title>
  <meta name="description" content="{meta['description'][:160]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
<div class="scroll-progress"></div>
{make_nav(skill_name)}
<div class="page skill-layout">
{make_sidebar(skill_name)}
  <div class="main-content">
    <div class="topbar">
      <div class="breadcrumb"><a href="{PREFIX}/">AI4Bio Skills</a> / {meta['name']}</div>
      <div class="topbar-actions"><a href="https://github.com/junior1p/awesome-ai4bio-skills" target="_blank">GitHub ↗</a></div>
    </div>
    <div class="skill-content">
      <h1>{meta['name']}</h1>
      <p class="desc">{meta['description']}</p>
      {content}
      {refs_html}
    </div>
    <footer>
      <a href="{PREFIX}/">AI4Bio Skills</a> · {datetime.now().year} · Built for the computational biology community
    </footer>
  </div>
</div>
<script>
// Scroll progress bar
window.addEventListener('scroll',()=>{{
  const bar=document.querySelector('.scroll-progress');
  const scrolled=window.scrollY/(document.body.scrollHeight-window.innerHeight)*100;
  bar.style.width=scrolled+'%';
}});
</script>
</body>
</html>"""


def index_page_html(skills_meta: dict) -> str:
    cat_blocks = []
    for cat_name, cat_skills in CATEGORIES.items():
        color = CAT_COLORS.get(cat_name, "blue")
        items = []
        for s in sorted(cat_skills):
            meta = skills_meta.get(s, {"name": s, "description": ""})
            desc = meta.get("description", "")
            desc_short = desc[:60] + "..." if len(desc) > 60 else desc
            items.append(f"""
        <a href="{PREFIX}/{s}.html">
          <span class="skill-name">{meta['name']}</span>
          <span class="skill-desc">{desc_short}</span>
        </a>""")
        cat_blocks.append(f"""
    <div class="cat-card">
      <div class="cat-header" style="background:var(--accent)">{cat_name}</div>
      <div class="cat-items">{"".join(items)}</div>
    </div>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI4Bio Skills — {TOTAL_SKILLS} Computational Biology Skills for AI Agents</title>
  <meta name="description" content="Comprehensive library of computational biology and bioinformatics skills for AI agents. Covering genomics, protein design, single-cell analysis, drug discovery, and more.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
<div class="scroll-progress"></div>
{make_nav()}
<div class="page">
  <div class="hero">
    <div class="hero-grid"></div>
    <div class="hero-content">
      <div class="hero-label">Computational Biology Skills</div>
      <h1 class="hero-title"><em>AI4Bio</em> Skills</h1>
      <p class="hero-sub">A comprehensive library of executable skills for computational biology & bioinformatics AI agents. From protein language models to single-cell analysis, drug discovery to genomic pipelines — everything an AI agent needs to work with biological data.</p>
      <div class="hero-stats">
        <div class="stat-card"><div class="stat-num">{TOTAL_SKILLS}</div><div class="stat-label">Skills</div></div>
        <div class="stat-card"><div class="stat-num green">{len(CATEGORIES)}</div><div class="stat-label">Categories</div></div>
        <div class="stat-card"><div class="stat-num orange">MIT</div><div class="stat-label">License</div></div>
      </div>
    </div>
  </div>
  <div class="content-section">
    <div class="section-label">All Skills</div>
    <h2 class="section-title">Browse by Category</h2>
    <p class="section-sub">Click any skill to view detailed documentation, examples, and reference materials.</p>
    <div class="cat-grid">{"".join(cat_blocks)}</div>
  </div>
  <footer>
    <a href="{PREFIX}/">AI4Bio Skills</a> · {datetime.now().year} · <a href="https://github.com/junior1p/awesome-ai4bio-skills" target="_blank">GitHub</a> · MIT License
  </footer>
</div>
<script>
window.addEventListener('scroll',()=>{{
  const bar=document.querySelector('.scroll-progress');
  const scrolled=window.scrollY/(document.body.scrollHeight-window.innerHeight)*100;
  bar.style.width=scrolled+'%';
}});
</script>
</body>
</html>"""


# ─── Main ─────────────────────────────────────────────────────────────────

def generate():
    skills_meta = {}

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

    index_html = index_page_html(skills_meta)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"\n✅ index.html → {OUTPUT_DIR / 'index.html'}")

    (OUTPUT_DIR / "robots.txt").write_text("User-agent: *\nAllow: /\n")

    print(f"\n🎉 Site generated in {OUTPUT_DIR}")
    print(f"   All links use prefix: {PREFIX}/")


if __name__ == "__main__":
    generate()
