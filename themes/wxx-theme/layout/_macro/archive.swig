{% macro render() %}
<div id="primary">
  <section id="archive" class="archive"><p class="eyebrow">THE JOURNAL</p><h1 data-zh="文字归档" data-en="The archive">文字归档</h1>
    {% set year = "" %}
    {% if not page.prev %}
      {% if page.tag %}
        <div class="archive-title tag">
          <h2 class="archive-name">{{ taxonomy_label(page.tag) }}</h2>
        </div>
      {% elif page.category %}
        <div class="archive-title category">
          <h2 class="archive-name">{{ taxonomy_label(page.category) }}</h2>
        </div>
      {% endif %}
    {% endif %}

    {% for post in page.posts %}
      {% if page.archive %}
        {% set post.year = date(post.date, 'YYYY') %}

        {% if post.year !== year %}
          {% set year = post.year %}
          <div class="collection-title">
            <h2 class="archive-year">{{ year }}</h2>
          </div>
        {% endif %}
      {% endif %}

      <div class="archive-post">
        <span class="archive-post-time">
          {% if page.archive %}
            {{ date(post.date, 'MM.DD') }}
          {% else %}
            {{ date(post.date, 'YYYY-MM-DD') }}
          {% endif %}
        </span>
        <span class="archive-post-title">
          <a href="{{ url_for(post.path) }}" class="archive-post-link">
            {{ post.title }}
          </a>
        </span>
      </div>
    {% endfor %}
  </section>
 </div>

  {% include '../_partial/pagination.swig' %}
{% endmacro %}
