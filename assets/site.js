// Masonry layout, filters and the "what is your business" finder. No dependencies.
(() => {
  const grid = document.querySelector(".grid");
  if (!grid) return;
  const items = [...grid.querySelectorAll(".item")];
  const empty = document.querySelector(".empty");
  const reset = document.querySelector(".reset");
  const note = document.querySelector(".ask-note");
  const noteDefault = note ? note.textContent : "";
  const FA = (n) => String(n).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);
  const state = { kind: "", cat: "", match: null };
  const rtl = document.documentElement.dir === "rtl";

  // Fade each poster in once it has decoded, like the reference's blur-up.
  for (const img of grid.querySelectorAll("img.full")) {
    const done = () => img.classList.add("is-loaded");
    if (img.complete && img.naturalWidth) done();
    else img.addEventListener("load", done, { once: true });
  }

  const visible = (el) =>
    (!state.kind || el.dataset.kind === state.kind) &&
    (!state.cat || el.dataset.cat === state.cat) &&
    (!state.match || state.match.has(el.dataset.key));

  function layout() {
    const width = grid.clientWidth;
    if (width <= 0) return;
    const gap = width < 600 ? 12 : 20;
    const cols = Math.max(2, Math.min(5, Math.floor((width + gap) / (220 + gap))));
    const colw = (width - (cols - 1) * gap) / cols;
    const heights = new Array(cols).fill(0);
    grid.style.setProperty("--colw", colw + "px");
    for (const el of items) {
      if (!visible(el)) continue;
      const c = heights.indexOf(Math.min(...heights));
      const x = rtl ? width - colw - c * (colw + gap) : c * (colw + gap);
      el.style.setProperty("--pos", `translate(${x}px, ${heights[c]}px)`);
      heights[c] += colw * Number(el.dataset.ratio) + 44 + gap;
    }
    grid.style.height = Math.max(0, Math.max(...heights) - gap) + "px";
  }

  function apply() {
    let shown = 0;
    for (const el of items) {
      const on = visible(el);
      shown += on;
      el.classList.toggle("is-out", !on);
      el.setAttribute("aria-hidden", String(!on));
      el.querySelector("a").tabIndex = on ? 0 : -1;
      if (on) el.classList.remove("is-gone");
      else setTimeout(() => el.classList.contains("is-out") && el.classList.add("is-gone"), 300);
    }
    if (empty) empty.hidden = shown > 0;
    if (reset) reset.hidden = !(state.kind || state.cat || state.match);
    layout();
  }

  // Toggle groups: one pressed chip per group, pressing it again clears the group.
  for (const group of document.querySelectorAll("[data-filter]")) {
    const key = group.dataset.filter;
    group.addEventListener("click", (ev) => {
      const chip = ev.target.closest(".chip");
      if (!chip) return;
      const value = chip.getAttribute("aria-pressed") === "true" ? "" : chip.dataset.value;
      state[key] = value;
      for (const c of group.querySelectorAll(".chip")) c.setAttribute("aria-pressed", String(c.dataset.value === value && value !== ""));
      apply();
    });
  }

  function clearAll() {
    state.kind = state.cat = "";
    state.match = null;
    for (const c of document.querySelectorAll("[data-filter] .chip")) c.setAttribute("aria-pressed", "false");
    if (note) note.textContent = noteDefault;
    apply();
  }
  if (reset) reset.addEventListener("click", clearAll);
  if (empty) empty.querySelector("button")?.addEventListener("click", clearAll);
  for (const a of document.querySelectorAll("[data-show-kind]")) {
    a.addEventListener("click", () => {
      const chip = document.querySelector(`[data-filter="kind"] .chip[data-value="${a.dataset.showKind}"]`);
      if (chip && chip.getAttribute("aria-pressed") !== "true") chip.click();
    });
  }

  // Finder: match the typed business against each site's name, trade and tags.
  const form = document.querySelector(".ask");
  if (form) {
    const norm = (s) => s.replace(/[يى]/g, "ی").replace(/ك/g, "ک").replace(/‌/g, " ").toLowerCase();
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const words = norm(form.q.value).split(/[\s،,.]+/).filter((w) => w.length > 1);
      if (!words.length) { clearAll(); return; }
      const hits = new Set();
      for (const el of items) {
        const hay = norm(el.dataset.search);
        if (words.some((w) => hay.includes(w) || hay.split(" ").some((t) => t.length > 2 && w.includes(t)))) hits.add(el.dataset.key);
      }
      state.kind = state.cat = "";
      for (const c of document.querySelectorAll("[data-filter] .chip")) c.setAttribute("aria-pressed", "false");
      state.match = hits.size ? hits : null;
      if (note) note.textContent = hits.size
        ? `${FA(hits.size)} نمونهٔ نزدیک پیدا شد.`
        : "نمونهٔ دقیقی نداریم؛ طراحی اختصاصی دقیقاً برای همین است.";
      apply();
      document.getElementById("work").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
    });
  }

  grid.classList.add("is-masonry");
  layout();
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!still) items.forEach((el, i) => { el.style.setProperty("--delay", i * 40 + "ms"); el.classList.add("is-entering"); });
  setTimeout(() => { items.forEach((el) => el.classList.remove("is-entering")); grid.classList.add("is-ready"); }, still ? 0 : 1300);
  let lastWidth = grid.clientWidth;
  const relayout = () => { if (grid.clientWidth !== lastWidth) { lastWidth = grid.clientWidth; layout(); } };
  new ResizeObserver(relayout).observe(grid);
  addEventListener("resize", relayout);
})();
