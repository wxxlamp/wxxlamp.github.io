{% if not resume_analytics_page() %}
{% include "_analytics/baidu-analytics.swig" %}
{% include "_analytics/google-analytics.swig" %}
{% include "_analytics/clarity.swig" %}
{% endif %}
{% include "_analytics/umami.swig" %}
