/* Project pages: cursor, nav, reveal, reading progress, cover parallax,
   chapter rail, accordion gallery and lightbox. */
(() => {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const pad = (n) => String(n).padStart(2, "0");

  /* ── Cursor (homepage behaviour; hidden until the mouse moves, idles when still) ── */
  const cursor = document.querySelector(".cursor");
  const dot = document.querySelector(".cursor-dot");
  if (cursor && window.matchMedia("(pointer: fine)").matches) {
    document.body.classList.add("has-custom-cursor");
    let x = 0, y = 0, cx = 0, cy = 0, running = false;
    const loop = () => {
      cx += (x - cx) * 0.15; cy += (y - cy) * 0.15;
      cursor.style.left = cx + "px"; cursor.style.top = cy + "px";
      if (Math.abs(x - cx) + Math.abs(y - cy) > 0.1) requestAnimationFrame(loop);
      else running = false;
    };
    document.addEventListener("mousemove", (e) => {
      x = e.clientX; y = e.clientY;
      if (!cursor.classList.contains("live")) { cx = x; cy = y; cursor.classList.add("live"); dot.classList.add("live"); }
      dot.style.left = x + "px"; dot.style.top = y + "px";
      if (!running) { running = true; requestAnimationFrame(loop); }
    });
    document.addEventListener("mouseover", (e) => { if (e.target.closest(".hoverable")) cursor.classList.add("hovering"); });
    document.addEventListener("mouseout", (e) => { if (e.target.closest(".hoverable")) cursor.classList.remove("hovering"); });
  }

  /* ── Reveal ── */
  const targets = document.querySelectorAll(".reveal, .reveal-stagger");
  if (reduced || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("visible"));
  } else {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add("visible"); io.unobserve(en.target); }
    }), { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });
    targets.forEach((el) => io.observe(el));
  }

  /* ── Elements ── */
  const nav = document.querySelector(".nav");
  const bar = document.querySelector(".progress");
  const cover = document.querySelector(".cover img");
  const pin = document.querySelector(".acc-pin");
  const acc = document.querySelector(".acc");
  const panels = [...document.querySelectorAll(".acc-panel")];
  const count = document.querySelector(".g-count b");
  const pinned = window.matchMedia("(min-width: 769px)");
  let current = 0, lastScrollIdx = -1;

  function setPanel(i) {
    current = i;
    panels.forEach((p, k) => p.classList.toggle("on", k === i));
    if (count) count.textContent = pad(i + 1);
  }

  /* ── Scroll: measure on resize, then per frame read everything before writing ── */
  let docH = 0, pinSpan = 0;
  const measure = () => {
    docH = document.documentElement.scrollHeight - innerHeight;
    pinSpan = pin ? pin.offsetHeight - innerHeight : 0;
  };
  let ticking = false;
  function onScroll() {
    ticking = false;
    // reads
    const sy = window.scrollY;
    const coverRect = cover && !reduced ? cover.parentElement.getBoundingClientRect() : null;
    const pinTop = pin && pinned.matches ? pin.getBoundingClientRect().top : null;
    const focusInAcc = acc && acc.contains(document.activeElement);
    // writes
    if (nav) nav.classList.toggle("scrolled", sy > 100);
    if (bar) bar.style.transform = `scaleX(${docH > 0 ? Math.min(1, sy / docH) : 0})`;
    if (coverRect && coverRect.bottom > 0 && coverRect.top < innerHeight) {
      const t = Math.min(1, Math.max(0, (innerHeight - coverRect.top) / (innerHeight + coverRect.height)));
      cover.style.setProperty("--py", `${(-t * 15).toFixed(2)}%`);
    }
    if (pinTop !== null && pinSpan > 0 && panels.length && !focusInAcc) {
      const p = Math.min(0.9999, Math.max(0, -pinTop / pinSpan));
      const i = Math.floor(p * panels.length);
      if (i !== lastScrollIdx) { lastScrollIdx = i; setPanel(i); }
    }
  }
  const request = () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } };
  addEventListener("scroll", request, { passive: true });
  addEventListener("resize", () => { measure(); request(); });
  addEventListener("load", () => { measure(); request(); });
  measure();
  onScroll();

  /* ── Lightbox ── */
  const srcs = panels.map((p) => p.dataset.full);
  const page = [document.querySelector(".nav"), document.querySelector("main"), document.querySelector(".footer")].filter(Boolean);
  let lb, lbImg, lbCount, li = 0, opener = null;
  function buildLightbox() {
    lb = document.createElement("div");
    lb.className = "lb";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Image viewer");
    lb.innerHTML =
      '<img alt="" />' +
      '<button type="button" class="lb-close hoverable" aria-label="Close viewer"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg></button>' +
      '<button type="button" class="lb-prev hoverable" aria-label="Previous image"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M5 12L12 19M5 12L12 5"/></svg></button>' +
      '<button type="button" class="lb-next hoverable" aria-label="Next image"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12H19M19 12L12 5M19 12L12 19"/></svg></button>' +
      '<span class="lb-count" aria-live="polite"></span>';
    document.body.appendChild(lb);
    lbImg = lb.querySelector("img");
    lbCount = lb.querySelector(".lb-count");
    lb.querySelector(".lb-close").addEventListener("click", closeLb);
    lb.querySelector(".lb-prev").addEventListener("click", () => showLb(li - 1));
    lb.querySelector(".lb-next").addEventListener("click", () => showLb(li + 1));
    lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
    document.addEventListener("keydown", (e) => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") closeLb();
      if (e.key === "ArrowRight") showLb(li + 1);
      if (e.key === "ArrowLeft") showLb(li - 1);
      if (e.key === "Tab") { // keep focus inside the dialog
        const f = [...lb.querySelectorAll("button")];
        const idx = f.indexOf(document.activeElement);
        e.preventDefault();
        f[(idx + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });
  }
  function showLb(i) {
    li = (i + srcs.length) % srcs.length;
    const alt = panels[li].dataset.alt || "";
    lbImg.src = srcs[li];
    lbImg.alt = alt;
    lbCount.textContent = `${pad(li + 1)} / ${pad(srcs.length)}`;
    lbCount.setAttribute("aria-label", `${alt}, image ${li + 1} of ${srcs.length}`);
  }
  function openLb(i) {
    if (!lb) buildLightbox();
    opener = document.activeElement;
    showLb(i);
    lb.classList.add("open");
    page.forEach((el) => (el.inert = true));
    document.body.style.overflow = "hidden";
    lb.querySelector(".lb-close").focus();
  }
  function closeLb() {
    lb.classList.remove("open");
    page.forEach((el) => (el.inert = false));
    document.body.style.overflow = "";
    if (opener && opener.focus) opener.focus({ preventScroll: true });
  }

  /* ── Accordion: hover / keyboard focus opens a panel; a tap or click on the open panel opens the lightbox ── */
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  panels.forEach((p, i) => {
    let wasOpen = false;
    p.addEventListener("pointerdown", () => { wasOpen = current === i; });
    p.addEventListener("mouseenter", () => { if (fine.matches && pinned.matches) setPanel(i); });
    p.addEventListener("focus", () => { if (p.matches(":focus-visible")) setPanel(i); });
    p.addEventListener("click", (e) => {
      const open = e.detail === 0 ? current === i : (fine.matches && pinned.matches) || wasOpen;
      if (open) openLb(i); else setPanel(i);
    });
  });
  if (panels.length) setPanel(0);

  /* ── Chapter rail ── */
  const links = [...document.querySelectorAll(".rail a")];
  if (links.length && "IntersectionObserver" in window) {
    const railIo = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((l) => {
          const on = l.getAttribute("href") === "#" + e.target.id;
          l.classList.toggle("active", on);
          if (on) l.setAttribute("aria-current", "location"); else l.removeAttribute("aria-current");
          if (on && innerWidth <= 1024) {
            const ol = l.closest("ol");
            ol.scrollTo({ left: l.offsetLeft - ol.clientWidth / 2 + l.offsetWidth / 2, behavior: reduced ? "auto" : "smooth" });
          }
        });
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    document.querySelectorAll("[data-chapter]").forEach((c) => railIo.observe(c));
  }
  links.forEach((l) => l.addEventListener("click", (e) => {
    const t = document.querySelector(l.getAttribute("href"));
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
    history.replaceState(null, "", l.getAttribute("href"));
  }));
})();
