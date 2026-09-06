{% if theme.widget.Categories %}
<section id="categories" class="widget-area widget_categories">
  <h3 class="widget-title" data-zh="按分类阅读" data-en="Categories">按分类阅读</h3>
  <ul class="category-list">
  {% for item in localized_taxonomy('categories') %}<li class="category-list-item"><a class="category-list-link" href="{{ url_for(item.path) }}">{{ taxonomy_label(item.name) }}</a><span class="category-list-count">{{ item.count }}</span></li>{% endfor %}
  </ul>
</section>
{% endif %}
