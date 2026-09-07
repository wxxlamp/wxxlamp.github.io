(function () {
  'use strict';
  var container = document.querySelector('[data-counter-origin]');
  if (!container || container.dataset.initialized) return;
  container.dataset.initialized = 'true';
  var status = container.querySelector('.site-stats__status');
  var counts = container.querySelector('.site-stats__counts');
  var english = document.documentElement.lang === 'en';
  var production = new URL(container.dataset.counterOrigin);
  // localhost and alternate/preview domains have their own shared counters.
  // Displaying those numbers as this blog's traffic is misleading.
  if (window.location.origin !== production.origin) {
    status.textContent = english ? 'Preview visits are not counted' : '预览访问不计数';
    return;
  }
  var pv = document.getElementById('busuanzi_value_site_pv');
  var uv = document.getElementById('busuanzi_value_site_uv');
  var finished = false;
  var observer = new MutationObserver(update);
  var timer = setTimeout(fail, 10000);
  function stop() {
    finished = true;
    observer.disconnect();
    clearTimeout(timer);
  }
  function fail() {
    if (finished) return;
    stop();
    status.textContent = english ? 'Stats temporarily unavailable' : '统计暂不可用';
  }
  function update() {
    if (finished) return;
    var values = [pv.textContent.trim(), uv.textContent.trim()];
    if (values.some(function (value) { return !/^\d+$/.test(value); })) return;
    if (values.some(function (value) { return !Number.isSafeInteger(Number(value)); }) || Number(values[1]) > Number(values[0])) {
      fail();
      return;
    }
    stop();
    counts.hidden = false;
    status.hidden = true;
  }
  observer.observe(counts, { childList: true, subtree: true, characterData: true });
  var script = document.createElement('script');
  script.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
  script.async = true;
  script.onerror = fail;
  document.head.appendChild(script);
})();
