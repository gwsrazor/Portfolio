/* Shared behaviour: cursor, nav, reveal. Mirrors the homepage scripts. */
(() => {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.__reducedMotion = reduced;

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
    document.addEventListener("mouseover", (e) => {
      if (e.target.closest(".hoverable")) cursor.classList.add("hovering");
    });
    document.addEventListener("mouseout", (e) => {
      if (e.target.closest(".hoverable")) cursor.classList.remove("hovering");
    });
  }

  const nav = document.querySelector(".nav");
  if (nav) {
    const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 100);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  const targets = document.querySelectorAll(".reveal, .reveal-stagger");
  if (reduced || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("visible"));
  } else {
    const io = new IntersectionObserver(
      (entries) => entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("visible"); io.unobserve(en.target); }
      }),
      { threshold: 0.15, rootMargin: "0px 0px -60px 0px" },
    );
    targets.forEach((el) => io.observe(el));
  }
})();

/* Lightbox: any [data-lb] element opens its data-lb image; ordered by DOM. */
(() => {
  const items = [...document.querySelectorAll("[data-lb]")];
  if (!items.length) return;
  const srcs = [...new Set(items.map((el) => el.dataset.lb))];
  const lb = document.createElement("div");
  lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", "Image viewer");
  lb.innerHTML = '<img alt="" /><button class="lb-close hoverable" aria-label="Close"><svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg></button><button class="lb-prev hoverable" aria-label="Previous"><svg viewBox="0 0 24 24"><path d="M19 12H5M5 12L12 19M5 12L12 5"/></svg></button><button class="lb-next hoverable" aria-label="Next"><svg viewBox="0 0 24 24"><path d="M5 12H19M19 12L12 5M19 12L12 19"/></svg></button><span class="lb-count"></span>';
  document.body.appendChild(lb);
  const img = lb.querySelector("img"), count = lb.querySelector(".lb-count");
  let i = 0;
  const show = () => { img.src = srcs[i]; count.textContent = `${String(i + 1).padStart(2, "0")} / ${String(srcs.length).padStart(2, "0")}`; };
  const open = (n) => { i = n; show(); lb.classList.add("open"); document.body.style.overflow = "hidden"; lb.querySelector(".lb-close").focus(); };
  const close = () => { lb.classList.remove("open"); document.body.style.overflow = ""; };
  window.__openLightbox = (src) => open(Math.max(0, srcs.indexOf(src)));
  items.forEach((el) => el.addEventListener("click", (e) => { if (el.dataset.lbManual) return; e.preventDefault(); open(srcs.indexOf(el.dataset.lb)); }));
  lb.querySelector(".lb-close").onclick = close;
  lb.querySelector(".lb-prev").onclick = () => { i = (i - 1 + srcs.length) % srcs.length; show(); };
  lb.querySelector(".lb-next").onclick = () => { i = (i + 1) % srcs.length; show(); };
  lb.addEventListener("click", (e) => { if (e.target === lb) close(); });
  document.addEventListener("keydown", (e) => {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowRight") lb.querySelector(".lb-next").click();
    if (e.key === "ArrowLeft") lb.querySelector(".lb-prev").click();
  });
})();
