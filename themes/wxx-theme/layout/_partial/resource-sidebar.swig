{% set resource_manifest = site.data['hkust-resources'] %}
<div class="resource-sidebar-head">
  <a class="resource-back" href="{{ url_for('/resources/') }}">{{ site_icon('arrow-left') }} 全部资料</a>
  <p class="resource-sidebar-kicker">HKUST</p>
  <h2>{{ resource_manifest.title }}</h2>
  <p>{{ resource_manifest.description }}</p>
</div>
<nav class="resource-tree" aria-label="HKUST 资料目录">
  <a class="resource-overview-link{% if page.resource_id === 'overview' %} is-active{% endif %}" href="{{ url_for('/resources/hkust-exam-papers/') }}"{% if page.resource_id === 'overview' %} aria-current="page"{% endif %}>{{ site_icon('book') }} 资料概览</a>
  {% for section in resource_manifest.sections %}
    {% set section_active = false %}
    {% if section.items %}
      {% for item in section.items %}{% if item.id === page.resource_id %}{% set section_active = true %}{% endif %}{% endfor %}
    {% endif %}
    {% if section.groups %}
      {% for group in section.groups %}{% for item in group.items %}{% if item.id === page.resource_id %}{% set section_active = true %}{% endif %}{% endfor %}{% endfor %}
    {% endif %}
    <details class="resource-section"{% if section_active or page.resource_id === 'overview' %} open{% endif %}>
      <summary>{{ section.title }} {{ site_icon('chevron') }}</summary>
      {% if section.items %}
        <ul>
          {% for item in section.items %}
            <li><a href="{{ url_for(item.href) }}"{% if item.id === page.resource_id %} class="is-active" aria-current="page"{% endif %}><span>{{ item.title }}</span><small>{% if item.kind === 'pdf' %}PDF{% else %}文章{% endif %}</small></a></li>
          {% endfor %}
        </ul>
      {% endif %}
      {% if section.groups %}
        {% for group in section.groups %}
          <p class="resource-group-title">{{ group.title }}</p>
          <ul>
            {% for item in group.items %}
              <li><a href="{{ url_for(item.href) }}"{% if item.id === page.resource_id %} class="is-active" aria-current="page"{% endif %}><span>{{ item.title }}</span><small>{% if item.kind === 'pdf' %}PDF{% else %}文章{% endif %}</small></a></li>
            {% endfor %}
          </ul>
        {% endfor %}
      {% endif %}
    </details>
  {% endfor %}
</nav>
