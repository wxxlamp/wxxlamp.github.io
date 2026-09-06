<div class="site-header-inner">
  <a href="{{ localized_path('/') }}" class="site-brand" aria-label="王星星的魔灯 · 首页" data-zh-label="王星星的魔灯 · 首页" data-en-label="Sibo's Blog · Home">
    <img class="brand-mark" src="{{ url_for('favicon.svg') }}" width="36" height="36" alt="" aria-hidden="true">
    <span class="brand-name" data-zh="王星星的魔灯" data-en="Sibo's Blog">王星星的魔灯</span>
  </a>
  <nav id="nav-top" aria-label="主导航" data-zh-label="主导航" data-en-label="Main navigation">
    <ul class="nav-top-items">
      <li><a href="{{ localized_path('/') }}" data-nav="home" data-zh="文章" data-en="Writing">文章</a></li>
      <li><a href="{{ localized_path('/archives/') }}" data-nav="archives" data-zh="归档" data-en="Archive">归档</a></li>
      <li><a href="{{ localized_path('/about/') }}" data-nav="about" data-zh="关于" data-en="About">关于</a></li>
      <li><a href="{{ url_for('/resume/') }}" data-nav="resume" data-resume-link data-zh="简历" data-en="Résumé">简历</a></li>
    </ul>
  </nav>
  <div class="language-switch" aria-label="Language">
    <a href="{{ language_url('zh') }}" data-language="zh" lang="zh-CN" aria-label="阅读中文版">中</a>
    {% if language_url("en") %}<a href="{{ language_url('en') }}" data-language="en" lang="en" aria-label="Read in English">EN</a>{% endif %}
  </div>
</div>
