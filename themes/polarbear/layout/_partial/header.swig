<div class="site-header-inner">
    <h1 class="site-title">
        <a href="{{ url_for('.') }}" class="logo">{{ config.title }}</a>
    </h1>

    <nav id="nav-top">
        {% if theme.menu %}
            <ul id="menu-top" class="nav-top-items">
                {% for name, path in theme.menu %}
                    <li class="menu-item">
                        <a href="{{ url_for(path) }}">
                            {% set itemName = 'menu.' + name.toLowerCase() %}
                            {% if itemName.startsWith('menu') %}
                                {{ name }}
                            {% else %}
                                {{ __(itemName) }}
                            {% endif %}
                        </a>
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
        {# RSS Subscribe Button #}
        <a href="{{ url_for('atom.xml') }}" class="subscribe-btn header-rss" title="订阅 RSS">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14">
                <path d="M3 3a1 1 0 0 1 1-1h.5a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V3zm0 4.5a1 1 0 0 1 1-1h.5a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-.5zm0 4.5a1 1 0 0 1 1-1h.5a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V12zm0 4.5a1 1 0 0 1 1-1h.5a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-.5zM8.5 3a1 1 0 0 1 1-1H19a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H9.5a1 1 0 0 1-1-1V3zm0 4.5a1 1 0 0 1 1-1H19a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H9.5a1 1 0 0 1-1-1v-.5zm0 4.5a1 1 0 0 1 1-1H19a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H9.5a1 1 0 0 1-1-1V12zm0 4.5a1 1 0 0 1 1-1H19a1 1 0 0 1 1 1v.5a1 1 0 0 1-1 1H9.5a1 1 0 0 1-1-1v-.5z" fill="currentColor"/>
            </svg>
            订阅
        </a>
  </nav>
</div>
