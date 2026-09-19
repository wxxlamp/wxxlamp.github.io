(function () {
  'use strict';
  var language = document.body.dataset.resumeLanguage || (document.body.dataset.contentLanguage === 'en' ? 'en' : 'zh');
  function setLanguage(next) {
    document.documentElement.lang = next === 'en' ? 'en' : 'zh-CN';
    document.querySelectorAll('[data-zh][data-en]').forEach(function (el) { el.textContent = el.dataset[next]; });
    document.querySelectorAll('[data-zh-label]').forEach(function (el) { el.setAttribute('aria-label', el.dataset[next + 'Label']); });
    document.querySelectorAll('[data-language]').forEach(function (el) {
      if (el.dataset.language === next) el.setAttribute('aria-current', 'true');
      else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-resume-link]').forEach(function (el) { el.href = next === 'en' ? '/resume-en/' : '/resume/'; });
  }
  setLanguage(language);
  document.querySelectorAll('[data-language]').forEach(function (link) {
    link.addEventListener('click', function () {
      try { localStorage.setItem('site_language', link.dataset.language); } catch (_) {}
    });
  });
  var path = window.location.pathname.replace(/^\/en(?=\/)/, '') || '/';
  document.querySelectorAll('[data-nav]').forEach(function (link) {
    var key = link.dataset.nav;
    var active = key === 'home' ? path === '/' || /^\/page\//.test(path) : path.indexOf('/' + key) === 0;
    if (active) link.setAttribute('aria-current', 'page');
  });
  document.querySelectorAll('[data-copy-feed]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var input = document.getElementById(button.dataset.copyFeed);
      var status = document.getElementById('feed-copy-status');
      try {
        await navigator.clipboard.writeText(input.value);
        status.textContent = language === 'en' ? 'Subscription URL copied.' : '订阅地址已复制。';
      } catch (_) {
        input.focus(); input.select();
        status.textContent = language === 'en' ? 'Select and copy the URL above.' : '请复制上方已选中的订阅地址。';
      }
    });
  });
  var resourceMenu = document.querySelector('.resource-menu-button');
  var resourceSidebar = document.getElementById('resource-sidebar');
  var resourceBackdrop = document.querySelector('.resource-drawer-backdrop');
  if (resourceMenu && resourceSidebar && resourceBackdrop) {
    var resourceClose = resourceSidebar.querySelector('.resource-drawer-close');
    function setResourceDrawer(open) {
      document.body.classList.toggle('resource-drawer-open', open);
      resourceMenu.setAttribute('aria-expanded', String(open));
      resourceBackdrop.hidden = !open;
      if (open) resourceClose.focus();
      else resourceMenu.focus();
    }
    resourceMenu.addEventListener('click', function () { setResourceDrawer(true); });
    resourceClose.addEventListener('click', function () { setResourceDrawer(false); });
    resourceBackdrop.addEventListener('click', function () { setResourceDrawer(false); });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && document.body.classList.contains('resource-drawer-open')) setResourceDrawer(false);
    });
    var activeResource = resourceSidebar.querySelector('[aria-current="page"]');
    if (activeResource) resourceSidebar.scrollTop = Math.max(0, activeResource.offsetTop - resourceSidebar.clientHeight / 2);
  }
  var resourceSidebarToggle = document.querySelector('.resource-sidebar-toggle');
  if (resourceSidebarToggle) {
    function setResourceSidebarCollapsed(collapsed) {
      var label = collapsed ? '展开目录' : '收起目录';
      document.body.classList.toggle('resource-sidebar-collapsed', collapsed);
      resourceSidebarToggle.setAttribute('aria-expanded', String(!collapsed));
      resourceSidebarToggle.setAttribute('aria-label', label);
      resourceSidebarToggle.setAttribute('title', label);
      try { localStorage.setItem('resource_sidebar_collapsed', String(collapsed)); } catch (_) {}
    }
    var sidebarCollapsed = false;
    try { sidebarCollapsed = localStorage.getItem('resource_sidebar_collapsed') === 'true'; } catch (_) {}
    setResourceSidebarCollapsed(sidebarCollapsed);
    resourceSidebarToggle.addEventListener('click', function () {
      setResourceSidebarCollapsed(!document.body.classList.contains('resource-sidebar-collapsed'));
    });
  }
  var content = document.querySelector('.view-post .post-content');
  var toc = document.getElementById('toc-list');
  if (!content || !toc) return;
  var headings = Array.from(content.querySelectorAll('h1, h2, h3, h4'));
  if (headings.length < 2) { document.getElementById('toc-container').hidden = true; }
  headings.forEach(function (heading, index) {
    if (!heading.id) heading.id = 'section-' + index;
    var li = document.createElement('li');
    li.className = 'toc-' + heading.tagName.toLowerCase();
    var a = document.createElement('a');
    a.href = '#' + encodeURIComponent(heading.id);
    a.textContent = heading.textContent;
    li.appendChild(a); toc.appendChild(li);
  });
  var details = document.querySelector('.toc-container details');
  details.open = !window.matchMedia('(max-width: 960px)').matches;
  var ticking = false;
  function updateReading() {
    var offset = document.getElementById('masthead').getBoundingClientRect().height + 30;
    var active = -1;
    headings.forEach(function (h, i) { if (h.getBoundingClientRect().top <= offset) active = i; });
    Array.from(toc.children).forEach(function (li, i) {
      li.classList.toggle('active', i === active);
      if (i === active) li.firstChild.setAttribute('aria-current', 'location');
      else li.firstChild.removeAttribute('aria-current');
    });
    var rect = content.getBoundingClientRect();
    var distance = rect.height - window.innerHeight + offset;
    var progress = Math.max(0, Math.min(1, (offset - rect.top) / Math.max(1, distance)));
    document.querySelector('.reading-progress').style.width = (progress * 100) + '%';
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(updateReading); } }, { passive: true });
  window.addEventListener('resize', updateReading);
  updateReading();
}());
