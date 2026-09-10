{% macro render(post) %}
  <article class="post">
    <header class="post-header">
      <div class="post-meta"><time datetime="{{ date(post.date, 'YYYY-MM-DD') }}">{{ date(post.date, 'YYYY.MM.DD') }}</time>{% for category in post.categories %}<a href="{{ url_for(category.path) }}">{{ taxonomy_label(category.name) }}</a>{% endfor %}</div>
      {% if is_home() %}<h2 class="post-title" lang="{{ post.lang || 'zh-CN' }}"><a class="post-link" href="{{ url_for(post.path) }}">{{ post.title }}</a></h2>{% else %}<h1 class="post-title">{{ post.title }}</h1>{% endif %}
      {% if not is_home() and theme.umami.enable and public_analytics_enabled() %}
      <div class="post-stats" data-page-counter>
        <span class="page-stats__counts" hidden title="自建 Umami 累计统计 / Self-hosted Umami cumulative statistics">
          <span data-zh="本文阅读（PV）" data-en="Article views (PV)">本文阅读（PV）</span> <span id="umami_page_pv"></span> ·
          <span data-zh="本文访客（UV）" data-en="Article visitors (UV)">本文访客（UV）</span> <span id="umami_page_uv"></span>
        </span>
        <span class="page-stats__status" role="status" data-zh="统计加载中…" data-en="Loading stats…">统计加载中…</span>
      </div>
      {% endif %}
    </header>
    {% if is_home() %}
      <div class="post-excerpt" lang="{{ post.lang || 'zh-CN' }}">{% if post.description %}{{ post.description }}{% else %}{{ truncate(strip_html(post.excerpt || post.content), {length: 120}) }}{% endif %}</div>
      <a class="read-entry" href="{{ url_for(post.path) }}" aria-label="{{ post.title }}"><span data-zh="阅读全文" data-en="Read entry">阅读全文</span> {{ site_icon('external') }}</a>
    {% else %}
      {% include '../_partial/translation.swig' %}
      <div class="post-content" lang="{{ post.lang || 'zh-CN' }}">{{ post.content }}</div>
      <footer class="post-footer">
        {% if post.tags and post.tags.length %}<div class="post-tags">{% for tag in post.tags %}<a href="{{ url_for(tag.path) }}">{{ taxonomy_label(tag.name) }}</a>{% endfor %}</div>{% endif %}
        {% include '../_partial/pagination.swig' %}
        {% include '../_partial/comments.swig' %}
      </footer>
    {% endif %}
  </article>
{% endmacro %}
