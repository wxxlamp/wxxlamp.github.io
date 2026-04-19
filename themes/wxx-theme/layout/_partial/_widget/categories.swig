{% if theme.widget.Categories %}
    <section id="categories" class="widget-area widget_categories">
        <h3 class="widget-title">Categories</h3>
        {{ list_categories({show_count: true, amount: 0, orderby: 'count', order: -1}) }}
    </section>
{% endif %}
