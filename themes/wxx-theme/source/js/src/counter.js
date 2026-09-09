(function () {
  'use strict';
  var container = document.querySelector('[data-counter-origin]');
  if (!container || container.dataset.initialized) return;
  container.dataset.initialized = 'true';
  var groups = [{ root: container, prefix: 'site-stats', scope: 'site' }];
  var article = document.querySelector('[data-page-counter]');
  if (article) groups.push({ root: article, prefix: 'page-stats', scope: 'page' });
  groups.forEach(function (group) {
    group.status = group.root.querySelector('.' + group.prefix + '__status');
    group.counts = group.root.querySelector('.' + group.prefix + '__counts');
    group.pv = document.getElementById('busuanzi_' + group.scope + '_pv');
    group.uv = document.getElementById('busuanzi_' + group.scope + '_uv');
  });
  var english = document.documentElement.lang === 'en';
  var production = new URL(container.dataset.counterOrigin);
  // localhost and alternate/preview domains have their own shared counters.
  // Displaying those numbers as this blog's traffic is misleading.
  if (window.location.origin !== production.origin) {
    groups.forEach(function (group) {
      group.status.textContent = english ? 'Preview visits are not counted' : '预览访问不计数';
    });
    return;
  }
  var observer = new MutationObserver(update);
  var timer = setTimeout(fail, 10000);
  function stop() {
    observer.disconnect();
    clearTimeout(timer);
  }
  function fail() {
    groups.forEach(function (group) {
      if (!group.done) {
        group.done = true;
        group.status.textContent = english ? 'Stats temporarily unavailable' : '统计暂不可用';
      }
    });
    stop();
  }
  function update() {
    groups.forEach(function (group) {
      if (group.done) return;
      var values = [group.pv.innerText || group.pv.textContent, group.uv.innerText || group.uv.textContent]
        .map(function (value) { return value.trim(); });
      if (values.some(function (value) { return !/^\d+$/.test(value); })) return;
      group.done = true;
      var valid = values.every(function (value) { return Number.isSafeInteger(Number(value)); }) && Number(values[1]) <= Number(values[0]);
      group.counts.hidden = !valid;
      group.status.hidden = valid;
      if (!valid) group.status.textContent = english ? 'Stats temporarily unavailable' : '统计暂不可用';
    });
    if (groups.every(function (group) { return group.done; })) stop();
  }
  groups.forEach(function (group) {
    observer.observe(group.counts, { childList: true, subtree: true, characterData: true });
  });
  var script = document.createElement('script');
  script.src = 'https://cdn.busuanzi.cc/busuanzi/3.6.9/busuanzi.min.js';
  script.async = true;
  script.onerror = fail;
  document.head.appendChild(script);
})();
