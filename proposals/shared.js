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
