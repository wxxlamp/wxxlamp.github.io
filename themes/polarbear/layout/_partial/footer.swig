<span class="copyright-year">
    {% set current = date(Date.now(), "YYYY") %}
        &copy;
    {% if theme.since and theme.since != current %}
        {{ theme.since }} -
    {% endif %}
    {{ current }}
    <span class="footer-author">{{ config.author }}.</span>
    <span class="power-by">
        {{ __('footer.powered', '<a class="hexo-link" href="https://hexo.io/">Hexo</a> and <a class="theme-link" href="https://github.com/frostfan/hexo-theme-polarbear">Polar Bear</a>') }}
    </span>
</span>
<span class="site-stats" style="display: block; margin-top: 8px; font-size: 0.85rem; color: #666;">
    累计访问 <span id="busuanzi_value_site_pv"><i class="fa fa-spinner fa-spin"></i></span> 次 ·
    累计有 <span id="busuanzi_value_site_uv"><i class="fa fa-spinner fa-spin"></i></span> 人访问
</span>
<script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
