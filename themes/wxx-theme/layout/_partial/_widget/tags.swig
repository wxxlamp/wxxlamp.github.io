{% if theme.widget.Tags %}
<section id="tags" class="widget-area widget_tags">
  <h3 class="widget-title" data-zh="话题索引" data-en="Topics">话题索引</h3>
  <ul class="tag-list">
  {% for item in localized_taxonomy('tags') %}<li class="tag-list-item"><a class="tag-list-link" href="{{ url_for(item.path) }}">{{ taxonomy_label(item.name) }}</a><span class="tag-list-count">{{ item.count }}</span></li>{% endfor %}
  </ul>
</section>
{% endif %}
