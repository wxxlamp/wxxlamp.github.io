{% extends "_layout.swig" %}

{% block title %} {{ page.title }} - {{ site_title() }} {% endblock %}

{% block content %}
    <div id="primary">
        <article class="post">
            <header class="post-header">
                <h1 class="post-title">
                    {{ page.title }}
                </h1>
            </header>
            <div class="post-content" lang="{{ content_language() }}">
                {{ page.content }}
            </div>
        </article>
    </div>
{% endblock %}
