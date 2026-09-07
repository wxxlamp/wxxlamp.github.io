{% if theme.giscus.enable and not is_home() and not is_archive() %}
<section class="github-comments" data-comments-repo="{{ theme.giscus.repo }}" data-comments-repo-id="{{ theme.giscus.repo_id }}" data-comments-category="{{ theme.giscus.category }}" data-comments-category-id="{{ theme.giscus.category_id }}" data-comments-lang="{{ content_language() }}">
  <h2 class="comments-title" data-zh="评论" data-en="Comments">评论</h2>
  <p class="comments-status" role="status" data-zh="正在加载评论…" data-en="Loading comments…">正在加载评论…</p>
  <button class="comments-retry" type="button" hidden data-zh="重新加载评论" data-en="Reload comments">重新加载评论</button>
  <div class="giscus"></div>
  <noscript>请启用 JavaScript 查看评论。Please enable JavaScript to view comments.</noscript>
</section>
<script defer src="{{ url_for('js/src/comments.js') }}?v={{ theme.version }}"></script>
{% endif %}
