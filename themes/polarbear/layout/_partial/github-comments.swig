{# GitHub Comments using Giscus #}
{% if not is_home() and not is_archive() %}
<div class="github-comments">
  <div class="comments-title">💬 评论</div>
  <p style="color: #666; font-size: 0.9em; margin-bottom: 1em;">
    评论功能需要<a href="https://github.com/apps/giscus" target="_blank" rel="noopener">安装 Giscus App</a>到您的 GitHub 仓库。
  </p>
  <script src="https://giscus.app/client.js"
    data-repo="wxxlamp/wxxlamp.github.io"
    data-repo-id="R_kgDOCiYteA"
    data-category="General"
    data-category-id="DIC_kwDOCiYteM4CelIo"
    data-mapping="pathname"
    data-strict="0"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="bottom"
    data-theme="light"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
  </script>
</div>
{% endif %}
