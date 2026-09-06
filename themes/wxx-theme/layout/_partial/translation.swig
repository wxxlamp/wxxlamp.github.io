{% if is_post() and translation_url(page) %}
<nav class="post-language" aria-label="Article language">
  {% if page.lang === 'en' %}<a href="{{ translation_url(page) }}" lang="zh-CN">中文原文 {{ site_icon('external') }}</a>{% else %}<a href="{{ translation_url(page) }}" lang="en">Read in English {{ site_icon('external') }}</a>{% endif %}
</nav>
{% endif %}
