<!DOCTYPE html>
{% set english = page.layout === 'resume-en' %}
<html lang="{% if english %}en{% else %}zh-CN{% endif %}">
<head>
  {% include '_partial/head.swig' %}
  <link rel="stylesheet" href="{{ url_for('css/resume.css') }}?v={{ theme.version }}">
</head>
<body class="resume-body" data-resume-language="{% if english %}en{% else %}zh{% endif %}">
  <header id="masthead">{% include '_partial/header.swig' %}</header>
  <main>
    <section class="password-page" id="passwordPage">
      <div class="lock-container">
        <p class="eyebrow">CURRICULUM VITAE</p>
        <h1>{{ page.name }}</h1>
        <p class="lock-subtitle" data-zh="一份关于经历、实践与成长的记录。" data-en="Experience, practice, and progress.">一份关于经历、实践与成长的记录。</p>
        <form id="resume-access-form">
          <label for="passwordInput" data-zh="访问密码" data-en="Access password">访问密码</label>
          <input type="password" id="passwordInput" autocomplete="current-password" required aria-describedby="errorMessage">
          <button type="submit" class="primary-button"><span data-zh="查看简历" data-en="View résumé">查看简历</span> {{ site_icon('arrow-right') }}</button>
          <p class="error" id="errorMessage" role="status" aria-live="polite"></p>
        </form>
        <a class="text-link" href="{{ localized_path('/about/') }}"><span data-zh="先了解一下我" data-en="Get to know me">先了解一下我</span> {{ site_icon('external') }}</a>
        <noscript><p>请启用 JavaScript 查看简历。 Enable JavaScript to view this résumé.</p></noscript>
      </div>
    </section>
    <section class="resume-page" id="resumePage" hidden>
      <div class="resume-toolbar">
        <span data-zh="个人简历" data-en="Curriculum vitae">个人简历</span>
        <div class="resume-actions">
          <a href="{% if english %}{{ url_for('/resume/') }}{% else %}{{ url_for('/resume-en/') }}{% endif %}" lang="{% if english %}zh-CN{% else %}en{% endif %}">{% if english %}中文{% else %}English{% endif %}</a>
          <button type="button" class="primary-button" id="print-resume">{{ site_icon('print') }} <span data-zh="打印 / 保存 PDF" data-en="Print / Save PDF">打印 / 保存 PDF</span></button>
        </div>
      </div>
      <p class="print-hint" data-zh="打印建议：A4 纸张、100% 缩放，关闭浏览器的页眉和页脚。" data-en="For printing: A4 paper, 100% scale, browser headers and footers off.">打印建议：A4 纸张、100% 缩放，关闭浏览器的页眉和页脚。</p>
      <article class="resume-container" lang="{% if english %}en{% else %}zh-CN{% endif %}">
        <header class="resume-header">
          <h1 class="resume-name" tabindex="-1">{{ page.name }}</h1>
          <div class="contact">
            <a href="mailto:{{ page.contact.email }}">{{ page.contact.email }}</a>
            <a href="tel:{{ page.contact.phone }}">{{ page.contact.phone }}</a>
            <span>{{ page.contact.birth }}</span>
            <a href="{{ page.contact.website }}">wxxlamp.cn</a>
          </div>
        </header>
        <section class="resume-section">
          <h2 class="section-title">{% if english %}Education{% else %}教育经历{% endif %}</h2>
          {% for edu in page.education %}
          <div class="resume-item education-item">
            <div class="item-header"><h3>{{ edu.school }}</h3><span class="item-date">{{ edu.date }}</span></div>
            <p class="item-subheader">{{ edu.major }}</p>
            <p>{{ edu.description }}</p>
          </div>
          {% endfor %}
        </section>
        <section class="resume-section">
          <h2 class="section-title">{% if english %}Experience{% else %}工作经历{% endif %}</h2>
          {% for job in page.experience %}
          <div class="resume-item">
            <div class="item-header"><h3>{{ job.company }}</h3><span class="item-date">{{ job.date }}</span></div>
            <p class="item-subheader">{{ job.title }}</p><p>{{ job.description }}</p>
          </div>
          {% endfor %}
        </section>
        <section class="resume-section projects-section">
          <h2 class="section-title">{% if english %}Selected projects{% else %}项目经历{% endif %}</h2>
          {% for project in page.projects %}
          <div class="resume-item project-item">
            <div class="item-header"><h3>{{ project.name }}</h3><span class="item-date">{{ project.date }}</span></div>
            <p class="project-description">{{ project.summary }}</p>
            <ul>{% for highlight in project.highlights %}<li>{{ highlight }}</li>{% endfor %}</ul>
            {% if project.related_posts %}
            <p class="resume-reading"><span class="resume-reading-label">{% if english %}Related writing{% else %}相关实践{% endif %}</span>{% for reference in project.related_posts %}<a href="{{ full_url_for(reference.path) }}" target="_blank" rel="noopener">{{ reference.title }} {{ site_icon('external') }}</a>{% endfor %}</p>
            {% endif %}
          </div>
          {% endfor %}
        </section>
        <section class="resume-section skills-section">
          <h2 class="section-title">{% if english %}Technical skills{% else %}专业技能{% endif %}</h2>
          <ul>{% for skill in page.skills %}<li>{{ skill }}</li>{% endfor %}</ul>
        </section>
      </article>
    </section>
  </main>
  <script src="{{ url_for('js/src/resume.js') }}?v={{ theme.version }}"></script>
</body>
</html>
