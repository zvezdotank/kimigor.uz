/**
 * Отдаёт занятость календаря для kimigor.uz.
 *
 * Наружу уходит только время «занято с … по …»: ни названий встреч,
 * ни участников, ни описаний. Всё остальное остаётся в календаре.
 *
 * Как поставить:
 *   1. script.google.com → «Новый проект», вставить этот файл целиком.
 *   2. Развернуть → Новое развёртывание → тип «Веб-приложение».
 *        Запуск от имени: Я
 *        Доступ:          Все (Anyone)
 *   3. Скопировать URL вида https://script.google.com/macros/s/…/exec
 *      и прислать его — он прописывается в CAL_URL в scripts/content.py.
 *
 * После правок скрипта развёртывание нужно обновлять (Развернуть → Управление
 * развёртываниями → карандаш → Версия: новая).
 */

var DAYS_AHEAD = 14;          // на сколько дней вперёд смотрим
var CALENDAR_ID = 'primary';  // 'primary' — основной календарь

function doGet() {
  var cal = CALENDAR_ID === 'primary'
    ? CalendarApp.getDefaultCalendar()
    : CalendarApp.getCalendarById(CALENDAR_ID);

  var from = new Date();
  var to = new Date(from.getTime() + DAYS_AHEAD * 24 * 3600 * 1000);

  var busy = cal.getEvents(from, to)
    .filter(function (ev) {
      if (ev.isAllDayEvent()) return false;          // «весь день» занятостью не считаем
      if (ev.getTransparency && ev.getTransparency() === CalendarApp.EventTransparency.TRANSPARENT) {
        return false;                                 // помеченные как «свободен»
      }
      try {
        return ev.getMyStatus() !== CalendarApp.GuestStatus.NO;  // отклонённые не показываем
      } catch (e) {
        return true;                                  // событие без гостей
      }
    })
    .map(function (ev) {
      return { s: ev.getStartTime().toISOString(), e: ev.getEndTime().toISOString() };
    });

  var payload = {
    tz: cal.getTimeZone(),
    from: from.toISOString(),
    days: DAYS_AHEAD,
    busy: busy
  };

  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
