{% extends '_layout.swig' %}
{% block title %}{{ page.title }} - {{ site_title() }}{% endblock %}
{% block content %}
<div id="primary" class="subscribe-page">
  <p class="eyebrow">FOLLOW THE JOURNAL</p>
  <h1 data-zh="让新文章，来找你。" data-en="Let new entries come to you.">让新文章，来找你。</h1>
  <p data-zh="将订阅地址添加到你的 RSS 阅读器，就能收到最新文章。无需注册，提供完整正文。" data-en="Add a feed URL to your RSS reader to receive new articles in full. No account required.">将订阅地址添加到你的 RSS 阅读器，就能收到最新文章。无需注册，提供完整正文。</p>
  <div class="feed-options">
  {% for format in ['atom', 'rss'] %}
    <section class="feed-option">
      <h2>{% if format === 'atom' %}Atom{% else %}RSS 2.0{% endif %}</h2>
      <p data-zh="订阅当前语言的最新文章。复制地址后，在阅读器中选择「添加订阅」。" data-en="Subscribe to the latest entries in this language. Copy the URL, then choose Add feed in your reader.">订阅当前语言的最新文章。复制地址后，在阅读器中选择「添加订阅」。</p>
      <label for="feed-{{ format }}" data-zh="订阅地址" data-en="Feed URL">订阅地址</label>
      <div class="feed-copy"><input id="feed-{{ format }}" readonly value="{{ config.url }}{% if page.lang === 'en' %}/en{% endif %}/{{ format }}.xml"><button type="button" data-copy-feed="feed-{{ format }}" data-zh="复制" data-en="Copy">复制</button></div>
      <a class="text-link" href="{% if page.lang === 'en' %}/en{% endif %}/{{ format }}.xml"><span data-zh="查看 XML" data-en="View XML">查看 XML</span> {{ site_icon('external') }}</a>
    </section>
  {% endfor %}
  </div>
  <p id="feed-copy-status" role="status" aria-live="polite"></p>
</div>
{% endblock %}
