<!DOCTYPE html>
<html lang="{{ content_language() }}">
  <head>
    {% include '_partial/head.swig' %}
  </head>

  <body data-content-language="{{ content_language() }}" class="{% if is_home() %}view-home{% elif is_post() %}view-post{% else %}view-page{% endif %}">
    <a class="skip-link" href="#content" data-zh="跳至正文" data-en="Skip to content">跳至正文</a>
    <div id="page">
      <header id="masthead">
        {%- include '_partial/header.swig' %}
      </header>
      <main id="content" tabindex="-1">
        {% block content %}{% endblock %}
      </main>

      <footer id="colophon">
        {%- include '_partial/footer.swig' %}
      </footer>

      <button class="back-to-top" id="back-to-top" aria-label="回到顶部" data-zh-label="回到顶部" data-en-label="Back to top">{{ site_icon('arrow-up') }}</button>
    </div>
    {% include '_script/comments.swig' %}
    {% include '_script/libs.swig' %}
    {% include '_script/theme.swig' %}
  </body>
</html>
