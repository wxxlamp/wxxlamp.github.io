{% if theme.umami.enable and theme.umami.website_id and public_analytics_enabled() %}
<script defer src="{{ theme.umami.script_url }}"
  data-website-id="{{ theme.umami.website_id }}"
  data-domains="{{ theme.umami.domains }}"
  data-exclude-search="true"
  data-exclude-hash="true"></script>
{% endif %}
