{% if theme.widget.TagCategoryCloud %}
    <section id="tag-category-cloud" class="widget-area widget_tag_category_cloud">
        <h3 class="widget-title">标签分类云</h3>

        {% if theme.widget.Tags %}
            <div class="widget-tags">
                <h4 class="widget-subtitle">标签 (Tags)</h4>
                {{ list_tags({show_count: true, amount: 0, orderby: 'count', order: -1}) }}
            </div>
        {% endif %}

        {% if theme.widget.Categories %}
            <div class="widget-categories">
                <h4 class="widget-subtitle">分类 (Categories)</h4>
                {{ list_categories({show_count: true, amount: 0, orderby: 'count', order: -1}) }}
            </div>
        {% endif %}
    </section>
{% endif %}