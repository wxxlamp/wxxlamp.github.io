{% extends "_layout.swig" %}

{% block title %} {{ page.title }} - {{ site_title() }} {% endblock %}

{% block content %}
  <button class="resource-menu-button" type="button" aria-controls="resource-sidebar" aria-expanded="false">
    {{ site_icon('menu') }} <span>目录</span>
  </button>
  <div class="resource-drawer-backdrop" hidden></div>
  <div class="resource-shell">
    <button class="resource-sidebar-toggle" type="button" aria-controls="resource-sidebar" aria-expanded="true" aria-label="收起目录" title="收起目录">
      {{ site_icon('chevron') }}
    </button>
    <aside class="resource-sidebar" id="resource-sidebar">
      <button class="resource-drawer-close" type="button" aria-label="关闭目录">{{ site_icon('close') }}</button>
      {% include "_partial/resource-sidebar.swig" %}
    </aside>

    <article class="resource-document">
      <header class="resource-document-header">
        <nav class="resource-breadcrumb" aria-label="面包屑">
          <a href="{{ url_for('/resources/') }}">资料</a><span>/</span><a href="{{ url_for('/resources/hkust-exam-papers/') }}">HKUST</a>
          {% if page.resource_course %}<span>/</span><span>{{ page.resource_course }}</span>{% endif %}
        </nav>
        <h1>{{ page.title }}</h1>
        {% if theme.umami.enable and public_analytics_enabled() %}
          <div class="post-stats resource-page-stats" data-page-counter>
            <span class="page-stats__counts" hidden title="自建 Umami 累计统计">
              本页阅读（PV） <span id="umami_page_pv"></span> ·
              本页访客（UV） <span id="umami_page_uv"></span>
            </span>
            <span class="page-stats__status" role="status">统计加载中…</span>
          </div>
        {% endif %}
        {% if page.resource_kind %}
          <div class="resource-document-meta">
            <span>{% if page.resource_kind === 'pdf' %}PDF 文档{% else %}Markdown 文章{% endif %}</span>
            {% if page.resource_pages %}<span>{{ page.resource_pages }} 页</span>{% endif %}
            {% if page.resource_original %}
              <a href="{{ url_for(page.resource_original) }}"{% if page.resource_kind === 'pdf' %} download{% endif %}>
                {% if page.resource_kind === 'pdf' %}{{ site_icon('download') }} 下载原文件{% else %}{{ site_icon('external') }} 查看博客原文{% endif %}
              </a>
            {% endif %}
          </div>
          {% if page.resource_summary %}<p class="resource-file-summary">{{ page.resource_summary }}</p>{% endif %}
        {% endif %}
      </header>

      {% if page.resource_kind === 'pdf' %}
        <div class="resource-pdf-mobile-note">
          <span>移动端 PDF 预览取决于浏览器支持。</span>
          <a href="{{ url_for(page.resource_file) }}">在浏览器中打开</a>
        </div>
        <div class="resource-pdf-viewer">
          <object data="{{ url_for(page.resource_file) }}#view=FitH" type="application/pdf">
            <div class="resource-pdf-fallback">
              <p>当前浏览器无法在页面内显示 PDF。</p>
              <a class="resource-primary-action" href="{{ url_for(page.resource_file) }}">打开 PDF</a>
            </div>
          </object>
        </div>
      {% else %}
        <div class="post-content resource-markdown" lang="{{ content_language() }}">
          {{ page.content }}
        </div>
      {% endif %}

      {% include "_partial/resource-support.swig" %}

      {% if page.resource_previous or page.resource_next %}
        <nav class="resource-pagination" aria-label="资料翻页">
          {% if page.resource_previous %}<a href="{{ url_for(page.resource_previous.href) }}">{{ site_icon('arrow-left') }}<span><small>上一份</small>{{ page.resource_previous.title }}</span></a>{% else %}<span></span>{% endif %}
          {% if page.resource_next %}<a class="resource-next" href="{{ url_for(page.resource_next.href) }}"><span><small>下一份</small>{{ page.resource_next.title }}</span>{{ site_icon('arrow-right') }}</a>{% endif %}
        </nav>
      {% endif %}
    </article>
  </div>
{% endblock %}
