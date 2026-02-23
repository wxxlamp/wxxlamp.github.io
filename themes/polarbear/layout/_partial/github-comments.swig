{# GitHub Comments using Giscus #}
{% if not is_home() and not is_archive() %}
<div class="github-comments">
  <div class="comments-title">💬 Comments</div>
  <p style="color: #666; font-size: 0.9em; margin-bottom: 1em;">
    Comments require <a href="https://github.com/apps/giscus" target="_blank" rel="noopener">Giscus App</a> installed on your GitHub repository.
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
    data-lang="en"
    crossorigin="anonymous"
    async>
  </script>
</div>
{% endif %}
