<button class="search-open" type="button" aria-haspopup="dialog" aria-controls="site-search" aria-label="搜索" data-zh-label="搜索" data-en-label="Search"><svg class="site-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></svg></button>
<dialog id="site-search" class="search-dialog" aria-labelledby="search-title" data-index="{% if content_language() === 'en' %}{{ url_for('search/en.json') }}{% else %}{{ url_for('search/zh.json') }}{% endif %}">
  <div class="search-heading"><h2 id="search-title" data-zh="站内搜索" data-en="Search this site">站内搜索</h2><button type="button" class="search-close" data-zh="关闭" data-en="Close">关闭</button></div>
  <label for="search-query" data-zh="关键词、标题、代码、分类或标签" data-en="Keywords, titles, code, categories or tags">关键词、标题、代码、分类或标签</label>
  <input id="search-query" type="search" autocomplete="off" maxlength="160">
  <p id="search-status" role="status" aria-live="polite"></p>
  <button type="button" id="search-retry" hidden data-zh="重新加载" data-en="Try again">重新加载</button>
  <ol id="search-results"></ol>
  <button type="button" id="search-more" hidden data-zh="加载更多" data-en="Show more">加载更多</button>
</dialog>
<script defer src="{{ url_for('js/src/search-engine.js') }}?v=1"></script>
<script defer src="{{ url_for('js/src/search.js') }}?v=2"></script>
