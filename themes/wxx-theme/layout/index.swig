{% extends "_layout.swig" %}
{% import '_macro/post.swig' as post_template %}


{% block title %} {{ site_title() }} - {{ site_description() }}{% endblock %}

{% block content %}
    <section class="home-intro">
      <p class="eyebrow" data-zh="WXX / PERSONAL JOURNAL" data-en="SIBO / PERSONAL BLOG">WXX / PERSONAL JOURNAL</p>
      <h1 data-zh="勇士斗恶龙" data-en="Warrior Fights Dragons">勇士斗恶龙</h1>
      <p class="intro-description" data-zh="写代码，也写生活。记录工程实践、阅读见闻，以及一路走来的思考。" data-en="Notes on engineering, books, everyday life, and things learned along the way.">写代码，也写生活。记录工程实践、阅读见闻，以及一路走来的思考。</p>
      <a class="text-link" href="{{ localized_path('/about/') }}"><span data-zh="认识一下" data-en="A little about me">认识一下</span> {{ site_icon('arrow-right') }}</a>
    </section>
    <div id="primary" class="home">
      <div class="section-heading"><h2 data-zh="最近的文字" data-en="Recent writing">最近的文字</h2><span>{{ localized_post_count() }} <span data-zh="篇记录" data-en="entries">篇记录</span></span></div>
        {% for post in page.posts %}
            {{ post_template.render(post) }}
        {% endfor %}
        {% include "_partial/pagination.swig" %}
    </div>
    {% include "_partial/widget.swig" %}
{% endblock %}
