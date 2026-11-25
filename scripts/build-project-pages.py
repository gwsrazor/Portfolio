"""Rebuild the 8 project pages in the Chapters + Accordion layout (proposal B1).

Content (copy, metadata, images, prev/next, SEO head) is read from the
pre-redesign pages at git commit SOURCE_REF, so the script can be re-run
safely after layout tweaks:

    python3 scripts/build-project-pages.py

Styles and behaviour live in assets/project.css and assets/project.js.
"""
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

SOURCE_REF = "8eebf5e"  # last commit with the original project pages
ROOT = Path(__file__).resolve().parent.parent

# Homepage order (Selected Work)
ORDER = [
    "ac-milan-2026", "bein-sports", "icc", "qatar-2022",
    "the-open", "rmc-sport", "scg", "ac-milan-2015",
]

ARROW_UP = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M17 7H7M17 7V17" /></svg>'
ZOOM = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" /></svg>'
BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M5 12L12 19M5 12L12 5" /></svg>'


def source(slug):
    return subprocess.check_output(
        ["git", "show", f"{SOURCE_REF}:project-{slug}/index.html"], cwd=ROOT, text=True
    )


def inner(el):
    return re.sub(r"\s+", " ", el.decode_contents()).strip()


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ")).strip()


def build(slug):
    raw = source(slug)
    soup = BeautifulSoup(raw, "html.parser")

    # ── Head: keep SEO / JSON-LD, swap the inline <style> for the shared stylesheet
    head = raw[: raw.index("</head>")]
    head = re.sub(r"\s*<style>.*?</style>", '\n    <link rel="stylesheet" href="../assets/project.css" />', head, flags=re.S)
    head = head.replace("<!DOCTYPE html>", "<!doctype html>")

    eyebrow = text(soup.select_one(".project-hero-eyebrow"))
    title_html = inner(soup.select_one(".project-hero-title"))
    lines = [l.strip() for l in re.split(r"<br\s*/?>", title_html) if l.strip()]
    title_plain = " ".join(lines)
    subtitle = inner(soup.select_one(".project-hero-subtitle"))

    meta = {}
    for block in soup.select(".meta-block"):
        meta[text(block.select_one(".meta-label"))] = block.select_one(".meta-value")
    tags = [text(t) for t in meta["Deliverables"].select(".meta-tag")]
    cover = soup.select_one(".project-cover img")

    heading = inner(soup.select_one(".project-desc-heading"))
    paras = [inner(p) for p in soup.select(".project-desc-body p")]
    brief, challenge, approach = paras[0], paras[1], " ".join(paras[2:])

    imgs = [(img["src"], img.get("alt", "")) for img in soup.select(".gallery-item img")]

    nav_links = []
    for a in soup.select(".project-nav-link"):
        target = a["href"].strip("./").replace("project-", "").strip("/")
        nav_links.append((text(a.select_one(".project-nav-label")), text(a.select_one(".project-nav-name")), a["href"], target))

    idx = ORDER.index(slug) + 1
    def line(i, l):
        content = l if i == 0 else '<em class="accent">' + l + "</em>"
        return f'          <span class="line"><span>{content}</span></span>'

    title_lines = "\n".join(line(i, l) for i, l in enumerate(lines))
    # Fit the longest title line to its column (Syne 800 ≈ 0.74em per glyph)
    longest = max(len(re.sub(r"<[^>]+>", "", l)) for l in lines)
    fit_d = round(min(10, 86 / (longest * 0.86)), 2)
    fit_m = round(min(14, 86 / (longest * 0.86)), 2)
    tag_html = "".join(f'<li class="tag">{t}</li>' for t in tags)
    facts = "\n".join(
        f'          <div class="fact"><p class="label">{k}</p><p class="fact-value">{inner(meta[k])}</p></div>'
        for k in ("Client", "Year", "Role")
    )
    n = len(imgs)
    panels = "\n".join(
        f"""          <button type="button" class="acc-panel hoverable" data-full="{src}" data-alt="{alt}" aria-label="View image {i + 1:02d} of {n:02d} full screen: {alt}">
            <img src="{src}" alt="" loading="{'eager' if i == 0 else 'lazy'}" decoding="async" />
            <span class="acc-num" aria-hidden="true">({i + 1:02d})</span>
            <span class="acc-cap" aria-hidden="true"><b>({i + 1:02d})</b>View full screen<i>{ZOOM}</i></span>
          </button>"""
        for i, (src, alt) in enumerate(imgs)
    )
    pn = "\n".join(
        f"""        <a href="{href}" class="pn-row hoverable">
          <span class="eyebrow">{label.replace(' Project', ' project')}</span>
          <span class="pn-name">{name}</span>
          <span class="pn-thumb" aria-hidden="true"><img src="../images/{tslug}/card.webp" alt="" loading="lazy" /></span>
        </a>"""
        for label, name, href, tslug in nav_links
    )
    rail = """        <nav class="rail" aria-label="Chapters">
          <p class="label">Chapters</p>
          <ol>
            <li><a href="#brief" class="hoverable active"><span>01</span>Brief</a></li>
            <li><a href="#challenge" class="hoverable"><span>02</span>Challenge</a></li>
            <li><a href="#approach" class="hoverable"><span>03</span>Approach</a></li>
            <li><a href="#gallery" class="hoverable"><span>04</span>Gallery</a></li>
          </ol>
        </nav>"""

    body = f"""
  <body>
    <div class="progress" aria-hidden="true"></div>
    <div class="grain" aria-hidden="true"></div>
    <div class="cursor" aria-hidden="true"></div>
    <div class="cursor-dot" aria-hidden="true"></div>

    <nav class="nav" aria-label="Main navigation">
      <div class="container nav-inner">
        <a href="../" class="nav-logo hoverable"><img src="../logo.svg" alt="NB." width="47" height="36" /></a>
        <a href="../#work" class="back-link hoverable">{BACK} All Projects</a>
      </div>
    </nav>

    <main>
      <header class="hero container">
        <div class="hero-top">
          <p class="eyebrow">{eyebrow}</p>
          <p class="label">Case {idx:02d} / {len(ORDER):02d}</p>
        </div>
        <div class="hero-grid">
          <h1 class="hero-title" aria-label="{title_plain}" style="--fit-d: {fit_d}; --fit-m: {fit_m}">
{title_lines}
          </h1>
          <div class="hero-side">
            <p class="hero-sub">{subtitle}</p>
            <p class="label" id="deliverables">Deliverables</p>
            <ul class="tags" role="list" aria-labelledby="deliverables">{tag_html}</ul>
          </div>
        </div>
        <div class="facts reveal-stagger">
{facts}
        </div>
        <div class="cover reveal">
          <img src="{cover['src']}" alt="{cover.get('alt', '')}" width="{cover.get('width', '2544')}" height="{cover.get('height', '1090')}" fetchpriority="high" />
        </div>
      </header>

      <section class="body" aria-label="Case study">
        <div class="container body-grid">
{rail}
          <div class="chapters">
            <section class="chapter" id="brief" data-chapter aria-labelledby="brief-title">
              <p class="ch-num"><b>01</b><span>Brief</span></p>
              <h2 class="ch-title reveal" id="brief-title">{heading}</h2>
              <p class="ch-text reveal">{brief}</p>
            </section>
            <section class="chapter" id="challenge" data-chapter aria-labelledby="challenge-title">
              <h2 class="ch-num" id="challenge-title"><b>02</b><span>Challenge</span></h2>
              <p class="ch-lead reveal">{challenge}</p>
            </section>
            <section class="chapter" id="approach" data-chapter aria-labelledby="approach-title">
              <h2 class="ch-num" id="approach-title"><b>03</b><span>Approach</span></h2>
              <p class="ch-lead reveal">{approach}</p>
            </section>
          </div>
        </div>
      </section>

      <section class="gallery" id="gallery" data-chapter aria-label="Project gallery">
        <div class="acc-pin">
          <div class="acc-sticky">
            <div class="container g-head">
              <div>
                <p class="ch-num"><b>04</b><span>Gallery</span></p>
                <h2 class="ch-title">Project <span class="accent">gallery</span></h2>
              </div>
              <p class="g-hint"><span class="label">Scroll or hover to browse</span><span class="g-count" aria-hidden="true"><b>01</b><i> / {n:02d}</i></span></p>
            </div>
            <div class="acc">
{panels}
            </div>
          </div>
        </div>
      </section>

      <nav class="pn container" aria-label="More projects">
{pn}
      </nav>
    </main>

    <footer class="footer">
      <div class="container footer-inner">
        <p class="footer-copy">&copy; 2026 Nicolas Bousset. All rights reserved.</p>
        <ul class="footer-links">
          <li><a href="https://www.linkedin.com/in/nicolas-bousset-43657762/" target="_blank" rel="noopener noreferrer" class="hoverable">LinkedIn</a></li>
          <li><a href="https://www.behance.net/NicolasBousset/projects" target="_blank" rel="noopener noreferrer" class="hoverable">Behance</a></li>
        </ul>
      </div>
    </footer>

    <script src="../assets/project.js" defer></script>
  </body>
</html>
"""
    out = ROOT / f"project-{slug}" / "index.html"
    out.write_text(head.rstrip() + "\n  </head>" + body)
    print(f"built {out.relative_to(ROOT)}: {len(imgs)} images, {len(paras)} paragraphs, nav {[l[1] for l in nav_links]}")


if __name__ == "__main__":
    for s in ORDER:
        build(s)
