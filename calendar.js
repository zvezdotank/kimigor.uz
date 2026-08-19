/* Календарь занятости: тянет JSON из Apps Script и рисует сетку рабочих часов.
   Наружу приходит только время «занято с … по …», без названий встреч. */
(() => {
  const root = document.querySelector("[data-calendar]");
  if (!root) return;

  const URL_ = root.dataset.calendar;
  const TZ = root.dataset.tz || "Asia/Tashkent";
  const START = 9, END = 18, STEP = 60;   // рабочие часы и шаг сетки в минутах
  const DAYS = 14;
  const t = key => root.dataset[key] || "";

  const dayFmt = new Intl.DateTimeFormat(document.documentElement.lang || "ru",
    { timeZone: TZ, weekday: "short", day: "numeric" });
  const timeFmt = new Intl.DateTimeFormat("ru", { timeZone: TZ, hour: "2-digit", minute: "2-digit", hour12: false });
  const fullFmt = new Intl.DateTimeFormat(document.documentElement.lang || "ru",
    { timeZone: TZ, weekday: "long", day: "numeric", month: "long" });

  /* Части даты в нужном часовом поясе — чтобы сетка совпадала с ташкентским временем. */
  const parts = d => {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-GB", {
      timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hour12: false, weekday: "short"
    }).formatToParts(d).filter(x => x.type !== "literal").map(x => [x.type, x.value]));
    return { key: `${p.year}-${p.month}-${p.day}`, h: +p.hour, m: +p.minute, wd: p.weekday };
  };

  const fail = msg => { root.innerHTML = `<p class="cal-msg">${msg}</p>`; };

  fetch(URL_, { mode: "cors" })
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => render(data.busy || []))
    .catch(() => fail(t("errorText")));

  function render(busy) {
    const now = new Date();
    const days = [];
    for (let i = 0; i < DAYS; i++) {
      const d = new Date(now.getTime() + i * 86400000);
      const p = parts(d);
      days.push({ date: d, key: p.key, wd: p.wd, weekend: p.wd === "Sat" || p.wd === "Sun" });
    }

    /* Раскладываем занятость по получасовым ячейкам. */
    const taken = new Set();
    busy.forEach(b => {
      let s = new Date(b.s), e = new Date(b.e);
      for (let cur = s; cur < e; cur = new Date(cur.getTime() + STEP * 60000)) {
        const p = parts(cur);
        if (p.h >= START && p.h < END) taken.add(`${p.key}|${p.h}`);
      }
    });

    const slots = [];
    for (let h = START; h < END; h++) slots.push(h);

    let html = '<div class="cal">';
    html += '<div class="cal-row cal-head"><div class="cal-time"></div>';
    days.forEach(d => {
      html += `<div class="cal-day${d.weekend ? " off" : ""}">${dayFmt.format(d.date)}</div>`;
    });
    html += "</div>";

    slots.forEach(h => {
      html += `<div class="cal-row"><div class="cal-time mono">${String(h).padStart(2, "0")}</div>`;
      days.forEach(d => {
        const isBusy = taken.has(`${d.key}|${h}`);
        const cls = d.weekend ? "off" : isBusy ? "busy" : "free";
        html += `<div class="cal-cell ${cls}"></div>`;
      });
      html += "</div>";
    });
    html += "</div>";

    /* Ближайшее свободное окно в рабочее время. */
    let next = null;
    outer:
    for (const d of days) {
      if (d.weekend) continue;
      for (const h of slots) {
        const cell = new Date(d.date);
        if (taken.has(`${d.key}|${h}`)) continue;
        const p = parts(new Date());
        if (d.key === p.key && h <= p.h) continue;
        next = { day: d.date, h };
        break outer;
      }
    }
    const legend = `<div class="cal-legend">
      <span><i class="sw busy"></i>${t("busyText")}</span>
      <span><i class="sw free"></i>${t("freeText")}</span>
    </div>`;
    const soon = next
      ? `<p class="cal-next">${t("nextText")} <b>${fullFmt.format(next.day)}, ${String(next.h).padStart(2, "0")}:00</b></p>`
      : "";
    root.innerHTML = soon + html + legend;
  }
})();
