<div class="site-header-inner">
    <h1 class="site-title">
        <a href="{{ url_for('.') }}" class="logo">{{ config.title }}</a>
    </h1>

    <nav id="nav-top">
        {% if theme.menu %}
            <ul id="menu-top" class="nav-top-items">
                {% for name, path in theme.menu %}
                    {% if name === 'Resume' %}
                    <li class="menu-item menu-item-resume">
                        <span class="resume-nav-label">Resume</span>
                        <ul class="resume-lang-dropdown">
                            <li><a href="{{ url_for('/resume') }}">中文简历</a></li>
                            <li><a href="{{ url_for('/resume-en') }}">English</a></li>
                        </ul>
                    </li>
                    {% else %}
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
                    {% endif %}
                {% endfor %}
                <li class="menu-item">
                    <a href="{{ url_for('atom.xml') }}">RSS</a>
                </li>
            </ul>
        {% endif %}
  </nav>
</div>
