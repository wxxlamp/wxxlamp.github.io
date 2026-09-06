{% if not is_post() %}
  <nav class="pagination">
    {% if page.prev %}
      <a class="prev" href="{{ url_for(page.prev_link) }}">
        {{ site_icon('arrow-left') }}
        <span class="prev-text"><span data-zh="上一页" data-en="Previous">上一页</span></span>
      </a>
    {% endif %}
    {% if page.next %}
      <a class="next" href="{{ url_for(page.next_link) }}">
        <span class="next-text"><span data-zh="下一页" data-en="Next">下一页</span></span>
        {{ site_icon('arrow-right') }}
      </a>
    {% endif %}
  </nav>
{% else %}
  <nav class="post-nav">
    {% if page.prev.path %}
      <a class="prev" href="{{ url_for(page.prev.path) }}">
        {{ site_icon('arrow-left') }}
        <span class="prev-text nav-default">{{ page.prev.title }}</span>
        <span class="prev-text nav-mobile"><span data-zh="上一篇" data-en="Previous entry">上一篇</span></span>
      </a>
    {% endif %}
    {% if page.next.path %}
      <a class="next" href="{{ url_for(page.next.path) }}">
        <span class="next-text nav-default">{{ page.next.title }}</span>
        <span class="prev-text nav-mobile"><span data-zh="下一篇" data-en="Next entry">下一篇</span></span>
        {{ site_icon('arrow-right') }}
      </a>
    {% endif %}
  </nav>
{% endif %}