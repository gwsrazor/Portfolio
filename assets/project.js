/* Project pages: cursor, nav, reveal, reading progress, cover parallax,
   chapter rail, accordion gallery and lightbox. */
(() => {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Cursor (homepage behaviour) ── */
  const cursor = document.querySelector(".cursor");
  const dot = document.querySelector(".cursor-dot");
  if (cursor && window.matchMedia("(pointer: fine)").matches) {
    document.body.classList.add("has-custom-cursor");
    let x = 0, y = 0, cx = 0, cy = 0;
    document.addEventListener("mousemove", (e) => {
      x = e.clientX; y = e.clientY;
      dot.style.left = x + "px"; dot.style.top = y + "px";
    });
    (function loop() {
      cx += (x - cx) * 0.15; cy += (y - cy) * 0.15;
      cursor.style.left = cx + "px"; cursor.style.top = cy + "px";
      requestAnimationFrame(loop);
    })();
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

  /* ── Scroll-driven: nav, progress, cover parallax, accordion ── */
  const nav = document.querySelector(".nav");
  const bar = document.querySelector(".progress");
  const cover = document.querySelector(".cover img");
  const pin = document.querySelector(".acc-pin");
  const panels = [...document.querySelectorAll(".acc-panel")];
  const count = document.querySelector(".g-count b");
  const pinned = window.matchMedia("(min-width: 769px)");
  let current = 0, lastScrollIdx = -1;

  function setPanel(i) {
    current = i;
    panels.forEach((p, k) => {
      const on = k === i;
      p.classList.toggle("on", on);
      p.setAttribute("aria-expanded", String(on));
    });
    if (count) count.textContent = String(i + 1).padStart(2, "0");
  }

  let ticking = false;
  function onScroll() {
    ticking = false;
    const sy = window.scrollY;
    nav && nav.classList.toggle("scrolled", sy > 100);
    if (bar) {
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? sy / max : 0})`;
    }
    if (cover && !reduced) {
      const r = cover.parentElement.getBoundingClientRect();
      if (r.bottom > 0 && r.top < innerHeight) {
        const t = Math.min(1, Math.max(0, (innerHeight - r.top) / (innerHeight + r.height)));
        cover.style.setProperty("--py", `${(-t * 15).toFixed(2)}%`);
      }
    }
    if (pin && panels.length && pinned.matches) {
      const r = pin.getBoundingClientRect();
      const span = pin.offsetHeight - innerHeight;
      if (span > 0) {
        const p = Math.min(0.9999, Math.max(0, -r.top / span));
        const i = Math.floor(p * panels.length);
        if (i !== lastScrollIdx) { lastScrollIdx = i; setPanel(i); }
      }
    }
  }
  const request = () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } };
  addEventListener("scroll", request, { passive: true });
  addEventListener("resize", request);
  onScroll();

  /* ── Lightbox ── */
  const srcs = panels.map((p) => p.dataset.full);
  let lb, lbImg, lbCount, li = 0, opener = null;
  function buildLightbox() {
    lb = document.createElement("div");
    lb.className = "lb";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Image viewer");
    lb.innerHTML =
      '<img alt="" />' +
      '<button type="button" class="lb-close hoverable" aria-label="Close viewer"><svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg></button>' +
      '<button type="button" class="lb-prev hoverable" aria-label="Previous image"><svg viewBox="0 0 24 24"><path d="M19 12H5M5 12L12 19M5 12L12 5"/></svg></button>' +
      '<button type="button" class="lb-next hoverable" aria-label="Next image"><svg viewBox="0 0 24 24"><path d="M5 12H19M19 12L12 5M19 12L12 19"/></svg></button>' +
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
    lbImg.src = srcs[li];
    lbImg.alt = panels[li].querySelector("img").alt;
    lbCount.textContent = `${String(li + 1).padStart(2, "0")} / ${String(srcs.length).padStart(2, "0")}`;
  }
  function openLb(i) {
    if (!lb) buildLightbox();
    opener = document.activeElement;
    showLb(i);
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
    lb.querySelector(".lb-close").focus();
  }
  function closeLb() {
    lb.classList.remove("open");
    document.body.style.overflow = "";
    opener && opener.focus && opener.focus({ preventScroll: true });
  }

  /* ── Accordion interactions ── */
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  panels.forEach((p, i) => {
    p.addEventListener("mouseenter", () => { if (fine.matches && pinned.matches) setPanel(i); });
    p.addEventListener("focus", () => setPanel(i));
    p.addEventListener("click", () => { if (current === i) openLb(i); else setPanel(i); });
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
          if (on) l.setAttribute("aria-current", "true"); else l.removeAttribute("aria-current");
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
