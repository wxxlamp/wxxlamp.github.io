{% if theme.umami.enable and theme.umami.website_id and public_analytics_enabled() %}
<script async src="{{ theme.umami.script_url }}"
  data-website-id="{{ theme.umami.website_id }}"
  data-domains="{{ theme.umami.domains }}"
  data-exclude-search="true"
  data-exclude-hash="true"></script>
{% endif %}
{% if theme.umami.cloud.enable and theme.umami.cloud.website_id and public_analytics_enabled() %}
<script async src="{{ theme.umami.cloud.script_url }}"
  data-website-id="{{ theme.umami.cloud.website_id }}"
  data-domains="{{ theme.umami.domains }}"
  data-exclude-search="true"
  data-exclude-hash="true"></script>
{% endif %}
