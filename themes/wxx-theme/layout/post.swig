{% extends "_layout.swig" %}
{% import '_macro/post.swig' as post_template %}

{% block title %} {{ page.title }} - {{ site_title() }} {% endblock %}

{% block content %}
    <div id="primary">
        {{ post_template.render(page) }}
    </div>
    {% include "_partial/toc.swig" %}
{% endblock %}
