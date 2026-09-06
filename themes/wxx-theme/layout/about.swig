{% extends "_layout.swig" %}
{% block title %}{{ page.title }} - {{ site_title() }}{% endblock %}
{% block content %}
<div id="primary" class="about-page"><article class="post"><div class="post-content" lang="{{ content_language() }}">{{ page.content }}</div></article></div>
{% endblock %}
