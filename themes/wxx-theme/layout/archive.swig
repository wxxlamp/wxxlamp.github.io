{% extends "_layout.swig" %}
{% import '_macro/archive.swig' as archive_template %}

{% block title %}
  {% if page.archive %}
    {% if content_language() === 'en' %}Archive{% else %}{{ __('menu.archives') }}{% endif %} - {{ site_title() }}
  {% elif page.tag %}
    {{ taxonomy_label(page.tag) }} - {{ site_title() }}
  {% elif page.category %}
    {{ taxonomy_label(page.category) }} - {{ site_title() }}
  {% endif %}
{% endblock %}

{% block content %}
  {{ archive_template.render() }}
{% endblock %}
