/* Проверка горизонтального переполнения на всех страницах и ширинах.
   Вставить в консоль браузера на любой странице сайта. */
(async () => {
  const pages = ["/", "/career/", "/training/", "/speaking/", "/jury/", "/media/", "/contacts/",
                 "/en/", "/uz/"];
  const widths = [360, 375, 414, 640, 768, 900, 1024, 1280, 1440, 1920];
  const bust = "?nc=" + Date.now();
  const frame = document.createElement("iframe");
  frame.style.cssText = "position:fixed;left:-99999px;height:600px;border:0";
  document.body.appendChild(frame);
  const bad = [];
  for (const w of widths) {
    frame.style.width = w + "px";
    for (const p of pages) {
      frame.src = p + bust;
      await new Promise(r => (frame.onload = r));
      await new Promise(r => setTimeout(r, 120));
      const doc = frame.contentDocument, de = doc.documentElement;
      const extra = de.scrollWidth - de.clientWidth;
      if (extra > 1) {
        const guilty = [];
        doc.querySelectorAll("*").forEach(el => {
          const r = el.getBoundingClientRect();
          if (!r.width && !r.height) return;
          // элемент внутри собственного скроллера — это норма, а не ошибка
          let par = el.parentElement, inScroller = false;
          while (par && par !== doc.body) {
            if (getComputedStyle(par).overflowX !== "visible") { inScroller = true; break; }
            par = par.parentElement;
          }
          if (!inScroller && r.right > de.clientWidth + 1) {
            guilty.push(el.tagName.toLowerCase() +
              (el.className ? "." + String(el.className).trim().split(/\s+/)[0] : ""));
          }
        });
        bad.push(`${w}px ${p} → +${extra}px  ${[...new Set(guilty)].slice(0, 3).join(", ") ||
                 "(псевдоэлемент или фон)"}`);
      }
    }
  }
  frame.remove();
  console.log(bad.length ? bad.join("\n") : "переполнений нет");
})();
