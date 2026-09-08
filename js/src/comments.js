(function () {
  'use strict';
  var container = document.querySelector('[data-comments-repo]');
  if (!container || container.dataset.initialized) return;
  container.dataset.initialized = 'true';
  var status = container.querySelector('.comments-status');
  var retry = container.querySelector('.comments-retry');
  var english = container.dataset.commentsLang === 'en';

  async function load() {
    retry.hidden = true;
    status.hidden = false;
    status.textContent = english ? 'Loading comments…' : '正在加载评论…';
    try {
      // Use IDs verified by the maintainer. The giscus categories API is not
      // CORS-accessible from arbitrary blogs, so it cannot run in this loader.
      if (!container.dataset.commentsRepoId || !container.dataset.commentsCategoryId) {
        throw new Error('Missing giscus repository/category IDs');
      }
      var script = document.createElement('script');
      script.src = 'https://giscus.app/client.js';
      script.async = true;
      script.crossOrigin = 'anonymous';
      var attributes = {
        repo: container.dataset.commentsRepo, 'repo-id': container.dataset.commentsRepoId,
        category: container.dataset.commentsCategory, 'category-id': container.dataset.commentsCategoryId,
        mapping: 'pathname', strict: '0', 'reactions-enabled': '1',
        'emit-metadata': '0', 'input-position': 'bottom', theme: 'light',
        lang: english ? 'en' : 'zh-CN'
      };
      Object.keys(attributes).forEach(function (key) { script.setAttribute('data-' + key, attributes[key]); });
      await new Promise(function (resolve, reject) {
        var timer = setTimeout(function () {
          script.remove();
          reject(new Error('giscus client timed out'));
        }, 15000);
        script.onload = function () { clearTimeout(timer); resolve(); };
        script.onerror = function () { clearTimeout(timer); script.remove(); reject(new Error('giscus client failed')); };
        container.querySelector('.giscus').appendChild(script);
      });
      status.hidden = true;
    } catch (error) {
      console.warn('[comments]', error.message);
      status.textContent = english ? 'Comments are temporarily unavailable. Please try again later.' : '评论暂时不可用，请稍后重试。';
      retry.hidden = false;
    }
  }
  retry.addEventListener('click', load);
  load();
})();
