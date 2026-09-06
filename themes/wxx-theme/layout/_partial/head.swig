{# Website mata #}
{% include "./_head/meta.swig" %}

{# One discovery link per format, matching the current content language. #}
{{ feed_tag(localized_path('atom.xml'), {type: 'atom', title: 'Atom'}) }}
{{ feed_tag(localized_path('rss.xml'), {type: 'rss2', title: 'RSS 2.0'}) }}
{% if language_url('en') %}
<link rel="alternate" hreflang="zh-CN" href="{{ config.url }}{{ language_url('zh') }}">
<link rel="alternate" hreflang="en" href="{{ config.url }}{{ language_url('en') }}">
<link rel="alternate" hreflang="x-default" href="{{ config.url }}{{ language_url('zh') }}">
{% endif %}

{# Website favicon #}
{% if theme.favicon %}
  <link rel="shortcut icon" type="image/x-icon" href="{{ url_for(theme.favicon) }}?v={{ theme.version }}" />
{% endif %}
<link rel="icon" type="image/svg+xml" href="{{ url_for('favicon.svg') }}?v={{ theme.version }}">
<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('apple-touch-icon.png') }}?v={{ theme.version }}">
<meta name="theme-color" content="#244f43">

{# Theme styling #}
<link rel="stylesheet" type="text/css" href="{{ url_for('css/style.css') }}?v={{ theme.version }}" />
{# Fancybox styling #}
{% if theme.theme.fancybox %}
  <link rel="stylesheet" type="text/css" href="{{ url_for('lib/fancybox/jquery.fancybox.css') }}" />
{% endif %}

<script defer src="{{ url_for('js/src/site.js') }}?v={{ theme.version }}"></script>

{# Theme Configuration #}
{% include "../_script/config.swig" %}

{# Load the math renderer only on articles or pages explicitly requesting it. #}
{% if is_post() or page.mathjax %}
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
  };
</script>
<script id="MathJax-script" async src="{{ url_for('lib/mathjax/tex-chtml.js') }}"></script>
{% endif %}

{# Analytics #}
{% if not env.debug %}
  {% include "../_script/analytics.swig" %}
{% endif %}
