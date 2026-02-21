{# GitHub Comments using Giscus #}
{% if not is_home() and not is_archive() %}
<div class="github-comments">
  <div class="comments-title">💬 评论</div>
  <script src="https://giscus.app/client.js"
    data-repo="wxxlamp/wxxlamp.github.io"
    data-repo-id="MDEwOlJlcG9zaXRvcnkxNjk0MzQxMjA="
    data-category="Announcements"
    data-category-id="DIC_kwDOCiYteM4CelIo"
    data-mapping="pathname"
    data-strict="0"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="bottom"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
  </script>
</div>
{% endif %}
