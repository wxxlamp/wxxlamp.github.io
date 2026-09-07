<div class="footer-inner"><span>© {{ date(Date.now(), 'YYYY') }} {{ site_author() }} <span class="footer-dot">·</span> <span data-zh="保持好奇，认真生活。" data-en="Stay curious. Live thoughtfully.">保持好奇，认真生活。</span></span><a href="{{ localized_path('/subscribe/') }}">{{ site_icon('rss') }} RSS</a></div>
<div class="site-stats">
  {% if theme.busuanzi.enable %}
  <span class="site-stats__counter" data-counter-origin="{{ config.url }}">
    <span class="site-stats__counts" hidden title="不蒜子全站累计统计，非当前页面或今日数据 / Site-wide cumulative estimates by Busuanzi">
      <span data-zh="全站访问（PV）" data-en="Site views (PV)">全站访问（PV）</span> <span id="busuanzi_value_site_pv"></span> ·
      <span data-zh="全站访客（UV）" data-en="Site visitors (UV)">全站访客（UV）</span> <span id="busuanzi_value_site_uv"></span>
    </span>
    <span class="site-stats__status" role="status" data-zh="统计加载中…" data-en="Loading stats…">统计加载中…</span> ·
  </span>
  <script defer src="{{ url_for('js/src/counter.js') }}?v={{ theme.version }}"></script>
  {% endif %}
  Powered by <a href="https://hexo.io/" rel="noopener">Hexo</a>
</div>
