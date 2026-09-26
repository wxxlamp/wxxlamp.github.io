(function () {
  'use strict';
  var dialog = document.getElementById('site-search');
  if (!dialog) return;
  var en = document.documentElement.lang === 'en';
  var text = en ? {
    post: 'Article', page: 'Page', resource: 'Resource', category: 'Category', tag: 'Tag',
    loading: 'Loading search index…', error: 'Could not load search. Check your connection and try again.',
    hint: 'Search English articles, categories and tags. Separate keywords with spaces.', empty: 'No results. Try different or fewer keywords.'
  } : {
    post: '文章', page: '页面', resource: '资料', category: '分类', tag: '标签',
    loading: '正在加载搜索索引…', error: '搜索索引加载失败，请检查网络后重试。',
    hint: '搜索中文文章、资料及公开页面。多个关键词请用空格分隔。', empty: '没有找到结果，请换个关键词或减少关键词。'
  };
  var query = document.getElementById('search-query');
  var status = document.getElementById('search-status');
  var results = document.getElementById('search-results');
  var more = document.getElementById('search-more');
  var retry = document.getElementById('search-retry');
  var records, pending, matches = [], limit = 20, timer;
  function snippet(entry) {
    var body = entry.body || entry.description;
    var lower = SiteSearch.normalize(body);
    var positions = SiteSearch.normalize(query.value).trim().split(/\s+/).filter(Boolean).map(function (term) { return lower.indexOf(term); }).filter(function (i) { return i >= 0; });
    var start = positions.length ? Math.max(0, Math.min.apply(null, positions) - 45) : 0;
    return (start ? '…' : '') + body.slice(start, start + 190) + (body.length > start + 190 ? '…' : '');
  }
  function render() {
    results.replaceChildren();
    matches.slice(0, limit).forEach(function (match) {
      var entry = match.entry;
      var li = document.createElement('li');
      var a = document.createElement('a'); a.href = entry.url; a.textContent = entry.title;
      var meta = document.createElement('small'); meta.textContent = [text[entry.kind]].concat(entry.categories, entry.tags).join(' · ');
      var p = document.createElement('p'); p.textContent = snippet(entry);
      li.append(a, meta, p); results.appendChild(li);
    });
    more.hidden = matches.length <= limit;
  }
  function run() {
    if (!records) return;
    limit = 20;
    matches = SiteSearch.search(records, query.value);
    var active = query.value.trim();
    status.textContent = !active ? text.hint : matches.length ? (en ? matches.length + (matches.length === 1 ? ' result' : ' results') : '找到 ' + matches.length + ' 条结果') : text.empty;
    render();
  }
  function load() {
    if (records) { run(); return; }
    if (pending) return;
    status.textContent = text.loading; retry.hidden = true;
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 15000);
    pending = fetch(dialog.dataset.index, { signal: controller.signal }).then(function (response) {
      if (!response.ok) throw new Error('Search index unavailable');
      return response.json();
    }).then(function (entries) {
      records = SiteSearch.prepare(entries);
      run();
    }).catch(function () { status.textContent = text.error; retry.hidden = false; })
      .finally(function () { clearTimeout(timeout); pending = null; });
  }
  document.querySelector('.search-open').addEventListener('click', function () {
    dialog.showModal(); document.body.classList.add('search-active'); query.focus(); load();
  });
  dialog.querySelector('.search-close').addEventListener('click', function () { dialog.close(); });
  dialog.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') { event.preventDefault(); dialog.close(); }
  });
  dialog.addEventListener('close', function () { document.body.classList.remove('search-active'); });
  dialog.addEventListener('click', function (event) {
    var box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  query.addEventListener('input', function (event) { clearTimeout(timer); if (!event.isComposing) timer = setTimeout(run, 120); });
  query.addEventListener('compositionend', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
  more.addEventListener('click', function () { limit += 20; render(); });
  retry.addEventListener('click', load);
})();
