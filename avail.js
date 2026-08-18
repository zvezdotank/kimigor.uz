/* Индикатор рабочего времени: пн–пт 9:00–18:00 по Ташкенту.
   Считаем в часовом поясе Игоря, а не посетителя. */
(() => {
  const nodes = [...document.querySelectorAll("[data-avail]")];
  if (!nodes.length) return;
  const TZ = "Asia/Tashkent", START = 9, END = 18;
  const fmt = new Intl.DateTimeFormat("en-GB", {
    timeZone: TZ, weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false
  });
  const DAYS = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };

  const plural = (n, forms) => {
    const a = Math.abs(n) % 100, b = a % 10;
    if (a > 10 && a < 20) return forms[2];
    if (b > 1 && b < 5) return forms[1];
    if (b === 1) return forms[0];
    return forms[2];
  };

  function minutesUntilOpen(day, h, m) {
    if (day >= 1 && day <= 5 && h < START) return (START - h) * 60 - m;
    let days = 1, d = (day + 1) % 7;
    while (d === 0 || d === 6) { days++; d = (d + 1) % 7; }
    return days * 1440 - (h * 60 + m) + START * 60;
  }

  function human(el, mins) {
    const u = el.dataset.units ? el.dataset.units.split("|") : ["д", "ч", "мин"];
    const d = Math.floor(mins / 1440), h = Math.floor((mins % 1440) / 60), m = mins % 60;
    if (d > 0) return `${d} ${u[0]} ${h} ${u[1]}`;
    if (h > 0) return `${h} ${u[1]} ${m} ${u[2]}`;
    return `${m} ${u[2]}`;
  }

  function tick() {
    const parts = Object.fromEntries(
      fmt.formatToParts(new Date()).filter(x => x.type !== "literal").map(x => [x.type, x.value])
    );
    const day = DAYS[parts.weekday], h = +parts.hour, m = +parts.minute;
    const open = day >= 1 && day <= 5 && h >= START && h < END;
    const mins = open ? (END - h) * 60 - m : minutesUntilOpen(day, h, m);
    nodes.forEach(el => {
      el.dataset.state = open ? "on" : "off";
      const short = open ? el.dataset.on : el.dataset.off;
      const tail = open ? `${el.dataset.left} ${human(el, mins)}` : `${el.dataset.back} ${human(el, mins)}`;
      // в шапке коротко, на странице контактов — с обратным отсчётом
      el.querySelector("span").textContent = el.hasAttribute("data-full") ? `${short} · ${tail}` : short;
      if (!el.hasAttribute("data-full")) el.title = `${short} · ${tail}`;
    });
  }

  tick();
  setInterval(tick, 30000);
})();
