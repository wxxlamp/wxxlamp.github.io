(function () {
  'use strict';
  var container = document.querySelector('[data-counter-origin]');
  if (!container || container.dataset.initialized) return;
  container.dataset.initialized = 'true';
  var groups = [{ root: container, prefix: 'site-stats', scope: 'site' }];
  var article = document.querySelector('[data-page-counter]');
  if (article) groups.push({ root: article, prefix: 'page-stats', scope: 'page' });
  var english = document.documentElement.lang === 'en';
  groups.forEach(function (group) {
    group.status = group.root.querySelector('.' + group.prefix + '__status');
    group.counts = group.root.querySelector('.' + group.prefix + '__counts');
    group.pv = document.getElementById('umami_' + group.scope + '_pv');
    group.uv = document.getElementById('umami_' + group.scope + '_uv');
  });
  if (window.location.origin !== new URL(container.dataset.counterOrigin).origin) {
    groups.forEach(function (group) {
      group.status.textContent = english ? 'Preview visits are not counted' : '预览访问不计数';
    });
    return;
  }
  // Busuanzi continues collecting independently, but never supplies visible numbers.
  if (container.dataset.busuanzi === 'true') {
    var sink = document.createElement('div');
    sink.hidden = true;
    ['site_pv', 'site_uv', 'page_pv', 'page_uv'].forEach(function (key) {
      var value = document.createElement('span');
      value.id = 'busuanzi_' + key;
      sink.appendChild(value);
    });
    document.body.appendChild(sink);
    var script = document.createElement('script');
    script.src = 'https://cdn.busuanzi.cc/busuanzi/3.6.9/busuanzi.min.js';
    script.async = true;
    document.head.appendChild(script);
  }
  var controller = new AbortController();
  var settled = false;
  function fail(group) {
    group.counts.hidden = true;
    group.status.hidden = false;
    group.status.textContent = english ? 'Stats temporarily unavailable' : '统计暂不可用';
  }
  var timer = setTimeout(function () {
    settled = true;
    controller.abort();
    groups.forEach(fail);
  }, 10000);
  Promise.resolve().then(function () {
    var endpoint = new URL(container.dataset.countersUrl);
    if (article) endpoint.searchParams.set('path', window.location.pathname);
    return fetch(endpoint.href, { signal: controller.signal, credentials: 'omit' });
  }).then(function (response) {
    if (!response.ok) throw new Error('Stats unavailable');
    return response.json();
  }).then(function (data) {
    if (settled) return;
    if (data.source !== 'umami-self-hosted') throw new Error('Unexpected statistics source');
    groups.forEach(function (group) {
      var value = data[group.scope];
      if (!value || !Number.isSafeInteger(value.pv) || !Number.isSafeInteger(value.uv) ||
          value.pv < 0 || value.uv < 0 || value.uv > value.pv) {
        fail(group);
        return;
      }
      group.pv.textContent = String(value.pv);
      group.uv.textContent = String(value.uv);
      group.counts.hidden = false;
      group.status.hidden = true;
    });
  }).catch(function () {
    if (!settled) groups.forEach(fail);
  }).finally(function () {
    settled = true;
    clearTimeout(timer);
  });
})();
