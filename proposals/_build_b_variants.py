"""Builds the B (Chapters) gallery variations from b-chapters/index.html.

Run from the proposals/ folder: python3 _build_b_variants.py
Each variant keeps B's hero, figures, chapter rail and details, and swaps
chapter 04 (Screens) for a full-bleed gallery treatment.
"""
from pathlib import Path

BASE = Path("b-chapters/index.html").read_text()

SCREENS = [
    ("gallery-1", "Tournament hub", "Tournament hub, highlights and news"),
    ("gallery-4", "Live leaderboard", "Live leaderboard with inline scorecard"),
    ("gallery-3", "Players", "Players and round scorecards"),
    ("gallery-6", "Hole guide", "Hole guide and player profile"),
    ("gallery-2", "Onboarding", "Onboarding and sign-in"),
    ("gallery-5", "Tickets", "Tickets and digital wallet"),
]
IMG = "../../images/the-open/{}.webp"
ARROW = '<svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7V17" /></svg>'


def n(i):
    return f"{i + 1:02d}"


def cut(s, start, end):
    a = s.index(start)
    b = s.index(end, a) + len(end)
    return s[a:b]


RAIL = cut(BASE, '<aside class="rail"', "</aside>")
CH_123 = cut(BASE, '<article class="chapter" id="brief">', '<article class="chapter" id="screens">').rsplit("<article", 1)[0]
CH_5 = cut(BASE, '<article class="chapter" id="details">', "</article>")
BODY = cut(BASE, '<section class="body">', "</section>")

COMMON_CSS = """
    /* ── Gallery chapter (full-bleed) ── */
    .gchapter { position: relative; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); scroll-margin-top: 0; }
    .g-head { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--space-md); }
    .g-head .ch-title { margin-bottom: 0; }
    .g-hint { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted); white-space: nowrap; }
    .body--after { padding-top: var(--space-2xl); }
    .body--after .rail-title { visibility: hidden; }
    .tile-btn { appearance: none; border: 0; padding: 0; margin: 0; background: none; color: inherit; font: inherit; text-align: left; }
"""


def page(slug, title, label, css, gallery, js):
    s = BASE
    s = s.replace("<title>Proposal B: Chapters</title>", f"<title>Proposal {label}: {title}</title>")
    s = s.replace("  </style>", COMMON_CSS + css + "\n  </style>", 1)
    body = f"""<section class="body">
      <div class="container body-grid">
        {RAIL}
        <div class="chapters">
          {CH_123.strip()}
        </div>
      </div>
    </section>

{gallery}

    <section class="body body--after">
      <div class="container body-grid">
        {RAIL}
        <div class="chapters">
          {CH_5}
        </div>
      </div>
    </section>"""
    s = s.replace(BODY, body)
    s = s.replace('document.querySelectorAll(".chapter").forEach', 'document.querySelectorAll(".chapter, .gchapter").forEach')
    badge = cut(s, '<nav class="proposal-badge"', "</nav>")
    items = [("../", "All", "")] + [
        (f"../{v}/", k, f" · {t}") for k, v, t in [("B1", "b1-accordion", "Accordion"), ("B2", "b2-stack", "Stack"), ("B3", "b3-mosaic", "Mosaic")]
    ]
    links = "\n".join(
        f'    <a href="{h}" class="hoverable"{" aria-current=\"page\"" if h == f"../{slug}/" else ""}>{a}<span class="pb-name">{b}</span></a>'
        for h, a, b in items
    )
    s = s.replace(badge, f'<nav class="proposal-badge" aria-label="Proposals">\n{links}\n  </nav>')
    s = s.replace("  </script>\n</body>", js + "\n  </script>\n</body>")
    out = Path(slug) / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s)
    print("wrote", out)


# ═══════════════════════════════════════════════════════════════
# B1 — ACCORDION  (Design House chapter panels + twks accordion)
# ═══════════════════════════════════════════════════════════════
acc_panels = "\n".join(
    f"""            <button type="button" class="acc-panel tile-btn hoverable{' on' if i == 0 else ''}" data-lb="{IMG.format(f)}" data-lb-manual="1" aria-label="{long}">
              <img src="{IMG.format(f)}" alt="{long}" loading="{'eager' if i < 2 else 'lazy'}" />
              <span class="acc-num">({n(i)})</span>
              <span class="acc-cap"><b>({n(i)})</b><span>{short}</span><i>{ARROW}</i></span>
            </button>"""
    for i, (f, short, long) in enumerate(SCREENS)
)
B1_HTML = f"""    <section class="gchapter g-acc" id="screens" aria-label="Screens">
      <div class="acc-pin">
        <div class="acc-sticky">
          <div class="container g-head">
            <div><p class="ch-num">04 — Screens</p><h2 class="ch-title">Six screens, <span class="accent">one tournament day.</span></h2></div>
            <span class="g-hint">Scroll or hover · click to enlarge</span>
          </div>
          <div class="acc">
{acc_panels}
          </div>
        </div>
      </div>
    </section>"""
B1_CSS = """
    /* B1 — ACCORDION. Refs: Design House (chapter panels), twks (accordion) */
    .acc-pin { height: 340vh; }
    .acc-sticky { position: sticky; top: 0; height: 100vh; display: flex; flex-direction: column; justify-content: center; gap: var(--space-lg); padding-top: 4rem; }
    .acc { display: flex; gap: 10px; height: 64vh; padding: 0 clamp(1.5rem, 4vw, 4rem); }
    .acc-panel { position: relative; flex: 1 1 0; min-width: 0; overflow: hidden; border-radius: 4px; background: #f3f3f3; transition: flex-grow 0.9s var(--ease-out-expo); }
    .acc-panel.on { flex-grow: 7; }
    .acc-panel img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: grayscale(1) brightness(0.42) contrast(1.1); transform: scale(1.15); transition: filter .8s var(--ease-out-expo), transform 1.2s var(--ease-out-expo); }
    .acc-panel.on img { filter: none; transform: scale(1); }
    .acc-panel:not(.on):hover img { filter: grayscale(1) brightness(0.6); }
    .acc-num { position: absolute; left: 50%; bottom: 1.1rem; transform: translateX(-50%); font-family: var(--font-display); font-weight: 700; font-size: 0.8rem; color: var(--cream); transition: opacity .4s ease; }
    .acc-panel.on .acc-num { opacity: 0; }
    .acc-cap { position: absolute; left: 1rem; right: 1rem; bottom: 1rem; display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1rem; background: rgba(10,10,10,0.88); backdrop-filter: blur(10px); border-radius: 2px; color: var(--cream); font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0; transform: translateY(14px); transition: opacity .5s var(--ease-out-expo), transform .6s var(--ease-out-expo); white-space: nowrap; }
    .acc-cap b { font-family: var(--font-display); color: var(--vermillion); }
    .acc-cap span { flex: 1; overflow: hidden; text-overflow: ellipsis; border-bottom: 1px solid var(--border); padding-bottom: 2px; }
    .acc-cap i { width: 30px; height: 30px; border-radius: 50%; border: 1px solid var(--border); display: grid; place-items: center; flex: none; }
    .acc-cap svg { width: 13px; height: 13px; stroke: var(--cream); fill: none; stroke-width: 1.5; }
    .acc-panel.on .acc-cap { opacity: 1; transform: none; transition-delay: .25s; }
    @media (max-width: 900px) {
      .acc-pin { height: auto; }
      .acc-sticky { position: relative; height: auto; padding: var(--space-2xl) 0; }
      .g-hint { display: none; }
      .acc { flex-direction: column; height: auto; gap: 8px; }
      .acc-panel { flex: none; height: 64px; transition: height .8s var(--ease-out-expo); }
      .acc-panel.on { height: 58vh; }
      .acc-num { left: 1rem; bottom: 50%; transform: translateY(50%); }
    }
"""
B1_JS = """
    /* B1 accordion: scroll picks the open panel; hover / tap opens one; click open panel → lightbox */
    (() => {
      const pin = document.querySelector(".acc-pin");
      const panels = [...document.querySelectorAll(".acc-panel")];
      const desktop = matchMedia("(min-width: 901px)");
      let cur = 0, lastScrollIdx = -1;
      const set = (i) => { cur = i; panels.forEach((p, k) => p.classList.toggle("on", k === i)); };
      function onScroll() {
        if (!desktop.matches) return;
        const r = pin.getBoundingClientRect();
        const span = pin.offsetHeight - innerHeight;
        const p = Math.min(0.9999, Math.max(0, -r.top / span));
        const i = Math.floor(p * panels.length);
        if (i !== lastScrollIdx) { lastScrollIdx = i; set(i); }
      }
      addEventListener("scroll", onScroll, { passive: true });
      onScroll();
      panels.forEach((p, i) => {
        p.addEventListener("mouseenter", () => { if (desktop.matches) set(i); });
        p.addEventListener("click", () => { if (cur === i) window.__openLightbox(p.dataset.lb); else set(i); });
      });
    })();
"""

# ═══════════════════════════════════════════════════════════════
# B2 — STACK  (Radaville stacked cases + White Desert giant type)
# ═══════════════════════════════════════════════════════════════
st_cards = "\n".join(
    f"""            <button type="button" class="st-card tile-btn hoverable" data-lb="{IMG.format(f)}" aria-label="Enlarge: {long}">
              <img src="{IMG.format(f)}" alt="{long}" loading="{'eager' if i < 2 else 'lazy'}" />
            </button>"""
    for i, (f, short, long) in enumerate(SCREENS)
)
st_ticks = "\n".join(f'            <span class="st-tick"><b>[ {n(i)} ]</b><em>{short}</em></span>' for i, (f, short, long) in enumerate(SCREENS))
st_words = "|".join(s for _, s, _ in SCREENS)
B2_HTML = f"""    <section class="gchapter g-stack" id="screens" aria-label="Screens">
      <div class="st-pin">
        <div class="st-sticky">
          <div class="st-word" aria-hidden="true" data-words="{st_words}"><span>{SCREENS[0][1]}</span></div>
          <div class="container st-top">
            <p class="ch-num">04 — Screens</p>
            <span class="st-count" aria-live="polite">[ <b>01</b> — 06 ]</span>
          </div>
          <div class="st-deck">
{st_cards}
          </div>
          <div class="container st-ruler" aria-hidden="true">
            <span class="st-ind"></span>
{st_ticks}
          </div>
        </div>
      </div>
    </section>"""
B2_CSS = """
    /* B2 — STACK. Refs: Radaville (stacked featured cases, tick ruler), White Desert (giant type behind imagery) */
    .st-pin { height: 560vh; }
    .st-sticky { position: sticky; top: 0; height: 100vh; overflow: hidden; display: grid; grid-template-rows: auto 1fr auto; padding: 6rem 0 1.5rem; }
    .st-sticky > .container { width: 100%; }
    .st-top { display: flex; justify-content: space-between; align-items: baseline; position: relative; z-index: 3; }
    .st-top .ch-num { margin: 0; }
    .st-count { font-family: var(--font-display); font-size: 0.85rem; color: var(--text-muted); letter-spacing: 0.04em; }
    .st-count b { color: var(--cream); }
    .st-word { position: absolute; inset: 0; display: grid; place-items: center; z-index: 0; pointer-events: none; overflow: hidden; }
    .st-word span { font-family: var(--font-display); font-weight: 800; text-transform: uppercase; white-space: nowrap; font-size: clamp(3.5rem, 11vw, 13rem); letter-spacing: -0.05em; line-height: 1; color: transparent; -webkit-text-stroke: 1px rgba(232,220,200,0.16); transition: opacity .5s ease, filter .5s ease, transform .7s var(--ease-out-expo); }
    .st-word.swap span { opacity: 0; filter: blur(8px); transform: translateY(20px); }
    .st-deck { position: relative; z-index: 2; }
    .st-card { position: absolute; left: 50%; top: 52%; width: min(64vw, 1040px); height: min(54vh, 580px); margin: 0; border-radius: 6px; overflow: hidden; background: #f4f4f4; box-shadow: 0 -20px 60px rgba(0,0,0,0.5); transform-origin: 50% 0; will-change: transform; transform: translate(-50%, -50%) translateY(110vh); }
    .st-card img { width: 100%; height: 100%; object-fit: contain; }
    .st-card::after { content: ""; position: absolute; inset: 0; background: #0a0a0a; opacity: var(--dim, 0); pointer-events: none; }
    .st-ruler { position: relative; z-index: 3; display: grid; grid-template-columns: repeat(6, 1fr); border-top: 1px solid var(--border); padding-top: 0.7rem;
      background-image: repeating-linear-gradient(90deg, var(--border) 0 1px, transparent 1px 12px); background-size: 100% 6px; background-repeat: no-repeat; background-position: 0 0; }
    .st-ind { position: absolute; top: -1px; left: 0; height: 2px; width: calc(100% / 6); background: var(--vermillion); transform: translateX(calc(var(--i, 0) * 100%)); transition: transform .5s var(--ease-out-expo); }
    .st-tick { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); display: flex; gap: 0.6rem; transition: color .3s ease; }
    .st-tick b { font-family: var(--font-display); font-weight: 700; }
    .st-tick.on { color: var(--cream); }
    .st-tick.on b { color: var(--vermillion); }
    @media (max-width: 900px) {
      .st-pin { height: 480vh; }
      .st-card { width: 88vw; height: 46vh; }
      .st-tick em { display: none; }
      .st-word span { font-size: 18vw; }
    }
"""
B2_JS = """
    /* B2 stack: each screen slides up and lands on the deck; earlier ones tuck back and dim */
    (() => {
      const pin = document.querySelector(".st-pin");
      const cards = [...document.querySelectorAll(".st-card")];
      const ticks = [...document.querySelectorAll(".st-tick")];
      const ruler = document.querySelector(".st-ruler");
      const count = document.querySelector(".st-count b");
      const word = document.querySelector(".st-word");
      const words = word.dataset.words.split("|");
      let shown = 0;
      function onScroll() {
        const r = pin.getBoundingClientRect();
        const span = pin.offsetHeight - innerHeight;
        const p = Math.min(1, Math.max(0, -r.top / span));
        const t = p * (cards.length - 1) * 1.08;          // small hold at the end
        cards.forEach((c, i) => {
          const d = t - i;
          let y, s, dim, z = i;
          if (d < -1) { y = 110; s = 1; dim = 0; }
          else if (d < 0) { const e = 1 - Math.pow(-d, 2); y = 110 * (1 - e); s = 1; dim = 0; }
          else { const k = Math.min(d, 3); y = -2.6 * k; s = 1 - 0.06 * k; dim = Math.min(0.75, 0.22 * k); }
          c.style.transform = `translate(-50%, -50%) translateY(${y.toFixed(2)}vh) scale(${s.toFixed(4)})`;
          c.style.setProperty("--dim", dim.toFixed(3));
          c.style.zIndex = z;
          c.style.visibility = d > 3.5 ? "hidden" : "visible";
          c.tabIndex = Math.round(t) === i ? 0 : -1;
        });
        const cur = Math.max(0, Math.min(cards.length - 1, Math.round(t)));
        ruler.style.setProperty("--i", cur);
        ticks.forEach((tk, i) => tk.classList.toggle("on", i === cur));
        count.textContent = String(cur + 1).padStart(2, "0");
        if (cur !== shown) {
          shown = cur; word.classList.add("swap");
          setTimeout(() => { word.firstElementChild.textContent = words[shown]; word.classList.remove("swap"); }, 250);
        }
      }
      addEventListener("scroll", onScroll, { passive: true });
      addEventListener("resize", onScroll);
      onScroll();
    })();
"""

# ═══════════════════════════════════════════════════════════════
# B3 — MOSAIC  (OFFF Forum work grid + Spyker Cars cinematic parallax)
# ═══════════════════════════════════════════════════════════════
mo_tiles = "\n".join(
    f"""            <button type="button" class="mo-tile mo-t{i + 1} tile-btn hoverable" data-lb="{IMG.format(f)}" aria-label="Enlarge: {long}">
              <img src="{IMG.format(f)}" alt="{long}" loading="{'eager' if i < 2 else 'lazy'}" />
              <span class="mo-cap"><b>{n(i)}</b>{short}</span>
            </button>"""
    for i, (f, short, long) in enumerate(SCREENS)
)
B3_HTML = f"""    <section class="gchapter g-mosaic" id="screens" aria-label="Screens">
      <div class="mo-pin">
        <div class="mo-sticky">
          <div class="container g-head mo-head">
            <div><p class="ch-num">04 — Screens</p><h2 class="ch-title">The whole <span class="accent">tournament</span>, at a glance.</h2></div>
            <span class="g-hint">Click any screen to enlarge</span>
          </div>
          <div class="container mo-grid">
{mo_tiles}
          </div>
          <p class="mo-word" aria-hidden="true">Selected<br /><span class="accent">screens</span></p>
        </div>
      </div>
    </section>"""
B3_CSS = """
    /* B3 — MOSAIC. Refs: OFFF Forum (grid of work), Spyker Cars (cinematic, layered parallax) */
    .mo-pin { height: 320vh; }
    .mo-sticky { position: sticky; top: 0; height: 100vh; overflow: hidden; display: flex; flex-direction: column; justify-content: center; gap: var(--space-md); padding-top: 4.5rem; --e: 0; }
    .mo-head .ch-title { max-width: none; }
    .mo-head { opacity: var(--e); transform: translateY(calc(30px * (1 - var(--e)))); }
    .mo-grid { position: relative; display: grid; grid-template-columns: 1fr 1.35fr 1.35fr 1fr; grid-template-rows: repeat(3, 1fr); gap: 10px; height: 66vh; width: 100%; }
    .mo-tile { position: relative; overflow: hidden; border-radius: 4px; background: #f4f4f4; will-change: transform, opacity; }
    .mo-tile img { width: 100%; height: 100%; object-fit: cover; transition: transform 1s var(--ease-out-expo); }
    .mo-t1 { grid-column: 2 / 4; grid-row: 1 / 3; z-index: 2; }
    .mo-t2 { grid-column: 1 / 2; grid-row: 1 / 4; }
    .mo-t3 { grid-column: 4 / 5; grid-row: 1 / 2; }
    .mo-t4 { grid-column: 4 / 5; grid-row: 2 / 4; }
    .mo-t5 { grid-column: 2 / 3; grid-row: 3 / 4; }
    .mo-t6 { grid-column: 3 / 4; grid-row: 3 / 4; }
    .mo-t2 img, .mo-t4 img { object-position: 50% 30%; }
    .mo-cap { position: absolute; left: 0.75rem; bottom: 0.75rem; display: flex; gap: 0.5rem; align-items: center; padding: 0.4rem 0.7rem; background: rgba(10,10,10,0.88); color: var(--cream); font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 2px; opacity: 0; transform: translateY(8px); transition: all .45s var(--ease-out-expo); }
    .mo-cap b { font-family: var(--font-display); color: var(--vermillion); }
    .settled .mo-tile:hover img { transform: scale(1.05); }
    .settled .mo-tile:hover .mo-cap, .settled .mo-tile:focus-visible .mo-cap { opacity: 1; transform: none; }
    .mo-word { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) scale(calc(1 + 0.25 * var(--e))); z-index: 5; pointer-events: none; text-align: center;
      font-family: var(--font-display); font-weight: 800; text-transform: uppercase; color: var(--cream); mix-blend-mode: difference;
      font-size: clamp(3rem, 11vw, 12rem); line-height: 0.85; letter-spacing: -0.05em; opacity: calc(1 - 1.6 * var(--e)); }
    .mo-word .accent { text-transform: none; letter-spacing: -0.02em; }
    @media (max-width: 900px) {
      .mo-pin { height: auto; }
      .mo-sticky { position: relative; height: auto; padding: var(--space-2xl) 0; --e: 1; overflow: visible; }
      .mo-word { display: none; }
      .g-hint { display: none; }
      .mo-grid { grid-template-columns: 1fr 1fr; grid-template-rows: none; grid-auto-rows: 28vw; grid-auto-flow: dense; height: auto; }
      .mo-t1 { grid-column: 1 / -1; grid-row: span 2; }
      .mo-t2 { grid-column: 1 / 2; grid-row: span 3; }
      .mo-t3, .mo-t5, .mo-t6 { grid-column: 2 / 3; grid-row: span 1; }
      .mo-t4 { grid-column: 1 / -1; grid-row: span 2; }
      .mo-cap { opacity: 1; transform: none; }
    }
"""
B3_JS = """
    /* B3 mosaic: the hero screen starts full-bleed, then shrinks into the grid while the others fly in at different speeds */
    (() => {
      const pin = document.querySelector(".mo-pin");
      const sticky = document.querySelector(".mo-sticky");
      const tiles = [...document.querySelectorAll(".mo-tile")];
      const hero = tiles[0];
      const desktop = matchMedia("(min-width: 901px)");
      let rest = [];
      const clamp = (v) => Math.min(1, Math.max(0, v));
      const ease = (x) => 1 - Math.pow(1 - x, 3);
      function measure() {
        tiles.forEach((t) => (t.style.transform = "none"));
        const s = sticky.getBoundingClientRect();
        rest = tiles.map((t) => { const b = t.getBoundingClientRect(); return { cx: b.left + b.width / 2 - s.left, cy: b.top + b.height / 2 - s.top, w: b.width, h: b.height }; });
        tick();
      }
      function tick() {
        if (!desktop.matches) { tiles.forEach((t) => { t.style.transform = ""; t.style.opacity = ""; }); sticky.classList.add("settled"); return; }
        const r = pin.getBoundingClientRect();
        const span = pin.offsetHeight - innerHeight;
        const p = window.__reducedMotion ? 1 : clamp(-r.top / span);
        const e = ease(clamp(p / 0.75));
        sticky.style.setProperty("--e", e.toFixed(4));
        sticky.classList.toggle("settled", e > 0.98);
        const s = sticky.getBoundingClientRect();
        const H = rest[0];
        const s0 = Math.max(innerWidth / H.w, innerHeight / H.h);
        const dx = innerWidth / 2 - (s.left + H.cx), dy = innerHeight / 2 - (s.top + H.cy);
        hero.style.transform = `translate(${(dx * (1 - e)).toFixed(1)}px, ${(dy * (1 - e)).toFixed(1)}px) scale(${(1 + (s0 - 1) * (1 - e)).toFixed(4)})`;
        tiles.slice(1).forEach((t, k) => {
          const R = rest[k + 1];
          const vx = R.cx - H.cx, vy = R.cy - H.cy, len = Math.hypot(vx, vy) || 1;
          const local = ease(clamp((p - 0.12 - k * 0.04) / 0.6));   // staggered, different speeds = parallax depth
          const push = (1 - local) * (innerHeight * (0.55 + k * 0.08));
          t.style.transform = `translate(${(vx / len * push).toFixed(1)}px, ${(vy / len * push).toFixed(1)}px) scale(${(0.8 + 0.2 * local).toFixed(3)})`;
          t.style.opacity = local.toFixed(3);
        });
      }
      addEventListener("scroll", tick, { passive: true });
      addEventListener("resize", measure);
      addEventListener("load", measure);
      measure();
    })();
"""

page("b1-accordion", "Accordion", "B1", B1_CSS, B1_HTML, B1_JS)
page("b2-stack", "Stack", "B2", B2_CSS, B2_HTML, B2_JS)
page("b3-mosaic", "Mosaic", "B3", B3_CSS, B3_HTML, B3_JS)
