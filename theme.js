/* Тема: по умолчанию — системная, выбор пользователя запоминается.
   Файл подключён в <head> без defer, чтобы класс появился до первой отрисовки
   и страница не мигала тёмной перед светлой. */
(() => {
  const KEY = "theme";
  const root = document.documentElement;

  const saved = (() => {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  })();
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;

  const systemLight = () => matchMedia("(prefers-color-scheme: light)").matches;
  const current = () => root.dataset.theme || (systemLight() ? "light" : "dark");

  /* Цвет адресной строки на телефоне должен совпадать с фоном страницы. */
  const paintBrowserUI = () => {
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = current() === "light" ? "#edf0f4" : "#101114";
  };

  const sync = btn => {
    const light = current() === "light";
    btn.setAttribute("aria-pressed", String(light));
    btn.setAttribute("aria-label", light ? btn.dataset.toDark : btn.dataset.toLight);
    btn.title = light ? btn.dataset.toDark : btn.dataset.toLight;
  };

  document.addEventListener("DOMContentLoaded", () => {
    paintBrowserUI();
    const btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    sync(btn);
    btn.addEventListener("click", () => {
      root.dataset.theme = current() === "light" ? "dark" : "light";
      try { localStorage.setItem(KEY, root.dataset.theme); } catch (e) { /* приватный режим */ }
      paintBrowserUI();
      sync(btn);
    });
  });

  /* Пока пользователь не выбрал сам, следуем за системой на лету. */
  matchMedia("(prefers-color-scheme: light)").addEventListener("change", () => {
    if (!root.dataset.theme) paintBrowserUI();
  });
})();
