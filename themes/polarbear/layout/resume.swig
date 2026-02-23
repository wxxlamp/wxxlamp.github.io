{# Resume layout with password protection - extends main layout structure #}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{ page.name }} - 个人简历</title>
  {% include '_partial/head.swig' %}
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: "Helvetica Neue", "Microsoft YaHei", Arial, sans-serif;
      background: #ffffff;
      color: #000000;
      line-height: 1.6;
    }

    /* Lock screen overlay */
    .lock-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: #ffffff;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }

    .lock-container {
      background: #ffffff;
      padding: 2.5rem;
      border-radius: 16px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      max-width: 420px;
      width: 90%;
      text-align: center;
      position: relative;
      margin-top: -60px;
    }

    .app-title {
      font-size: 2.2rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
      color: #1e3a8a;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .app-subtitle {
      font-size: 1.1rem;
      color: #4b5563;
      margin-bottom: 1.8rem;
    }

    .lock-container input {
      width: 200px;
      padding: 0.8rem;
      border: 1px solid #ddd;
      border-radius: 0;
      font-size: 1rem;
      margin-bottom: 1.2rem;
      text-align: center;
      font-family: monospace;
      letter-spacing: 2px;
      background: #f8fafc;
      transition: all 0.3s ease;
    }

    .lock-container input:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    .lock-container button {
      width: 100%;
      padding: 1rem;
      background: #000000;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .lock-container button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 8px rgba(0,0,0,0.15);
      background: #1a1a1a;
    }

    .lock-container button:active {
      transform: translateY(0);
    }

    .lock-container button:disabled {
      opacity: 0.7;
      transform: none;
      cursor: not-allowed;
    }

    .error {
      color: #e53e3e;
      font-size: 0.9rem;
      margin-top: 0.8rem;
      min-height: 1.2rem;
      font-weight: 500;
    }

    /* Resume content styles */
    .resume {
      display: none;
      padding: 2rem;
      max-width: 850px;
      margin: 0 auto;
      background: white;
      margin-top: 2rem;
      box-shadow: 0 5px 25px rgba(0,0,0,0.08);
      border-radius: 12px;
    }

    .resume-header {
      text-align: center;
      margin-bottom: 2.5rem;
      padding-bottom: 1.2rem;
      border-bottom: 1px solid #eaeaea;
    }

    .resume-name {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #1e293b;
    }

    .contact {
      font-size: 1rem;
      color: #4b5563;
      margin-top: 0.5rem;
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .contact-item {
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }

    .contact a {
      color: #3b82f6;
      text-decoration: none;
      font-weight: 500;
    }

    .contact a:hover {
      text-decoration: underline;
    }

    .section-title {
      font-size: 1.5rem;
      font-weight: 700;
      margin: 2rem 0 1.2rem;
      color: #1e293b;
      padding-bottom: 0.4rem;
      border-bottom: 2px solid #3b82f6;
    }

    .item {
      margin-bottom: 1.6rem;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      font-weight: 700;
      font-size: 1.2rem;
      color: #1e293b;
      margin-bottom: 0.3rem;
    }

    .item-subheader {
      font-weight: 600;
      color: #334155;
      margin: 0.3rem 0 0.5rem;
      font-size: 1.05rem;
    }

    .item-date {
      color: #64748b;
      font-size: 0.98rem;
      font-weight: 500;
    }

    .item-content {
      margin-top: 0.6rem;
      color: #334155;
      line-height: 1.7;
      font-size: 1.02rem;
    }

    ul {
      padding-left: 1.8rem;
      margin-top: 0.8rem;
      margin-bottom: 0.5rem;
    }

    li {
      margin-bottom: 0.6rem;
      line-height: 1.65;
    }

    .project-description {
      margin: 0.9rem 0;
      font-weight: 600;
      color: #334155;
      line-height: 1.7;
      font-size: 1.03rem;
    }

    .highlight {
      font-weight: 700;
      color: #1e3a8a;
    }

    .highlight-blue {
      font-weight: 700;
      color: #1e40af;
    }

    .education-item {
      display: flex;
      flex-direction: column;
    }

    .education-header {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 0.3rem;
    }

    .school-name {
      font-weight: 700;
      font-size: 1.25rem;
      color: #1e293b;
    }

    .major {
      font-weight: 600;
      font-size: 1.05rem;
      color: #334155;
      opacity: 0.9;
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .lock-container {
      animation: fadeInUp 0.6s ease-out;
    }

    @media (max-width: 768px) {
      .resume {
        padding: 1.8rem;
      }

      .resume-name {
        font-size: 2.1rem;
      }

      .section-title {
        font-size: 1.35rem;
      }

      .item-header {
        flex-direction: column;
        gap: 0.3rem;
        align-items: flex-start;
      }

      .contact {
        font-size: 0.9rem;
        gap: 0.5rem;
      }

      .lock-container {
        padding: 1.8rem;
        margin-top: -40px;
      }

      .app-title {
        font-size: 1.8rem;
      }
    }
  </style>
</head>
<body>
  <div id="page">
    <!-- Site Header -->
    <header id="masthead">
      {%- include '_partial/header.swig' %}
    </header>

    <!-- Password Lock Overlay -->
    <div class="lock-overlay" id="lockOverlay">
      <div class="lock-container">
        <div class="app-title">王星星的魔灯</div>
        <div class="app-subtitle">个人简历 · 需要密码访问</div>
        <input type="password" id="passwordInput" autocomplete="off" autofocus />
        <button onclick="validatePassword()">确认访问</button>
        <div class="error" id="errorMessage"></div>
      </div>
    </div>

    <!-- Resume Content -->
    <div id="content">
      <div class="resume" id="resume">
        <div class="resume-header">
          <div class="resume-name">{{ page.name }}</div>
          <div class="contact">
            <span class="contact-item">📱 {{ page.contact.phone }}</span>
            <span class="contact-item">✉️ {{ page.contact.email }}</span>
            <span class="contact-item">🎂 {{ page.contact.birth }}</span>
            <span class="contact-item">🌐 <a href="{{ page.contact.website }}" target="_blank">wxxlamp.cn</a></span>
          </div>
        </div>

        <div class="section-title">教育背景</div>
        {% for edu in page.education %}
        <div class="item education-item">
          <div class="item-header">
            <div class="education-header">
              <span class="school-name"><strong>{{ edu.school }}</strong></span>
              <span class="major"><strong>{{ edu.major }}</strong></span>
            </div>
            <span class="item-date"><strong>{{ edu.date }}</strong></span>
          </div>
          <div class="item-content">{{ edu.description }}</div>
        </div>
        {% endfor %}

        <div class="section-title">工作经历</div>
        <div class="item">
          <div class="item-header">
            <span><strong>{{ page.experience[0].company }}</strong></span>
            <span class="item-date"><strong>{{ page.experience[0].date }}</strong></span>
          </div>
          <div class="item-subheader"><strong>{{ page.experience[0].title }}</strong></div>
          <div class="item-content">{{ page.experience[0].description }}</div>
        </div>

        <div class="section-title">项目经历</div>
        {% for project in page.projects %}
        <div class="item">
          <div class="item-header">
            <span><strong>{{ project.name }}</strong></span>
            <span class="item-date"><strong>{{ project.date }}</strong></span>
          </div>
          <div class="project-description">项目描述：{{ project.summary }}</div>
          <div class="item-content">
            <ul>
              {% for highlight in project.highlights %}
              <li>{{ highlight }}</li>
              {% endfor %}
            </ul>
          </div>
        </div>
        {% endfor %}

        <div class="section-title">专业技术</div>
        <div class="item-content">
          <ul>
            {% for skill in page.skills %}
            <li>{{ skill }}</li>
            {% endfor %}
          </ul>
        </div>
      </div>
    </div>

    <footer id="colophon">
      {%- include '_partial/footer.swig' %}
    </footer>

    <div class="back-to-top" id="back-to-top">
      <i class="iconfont icon-up"></i>
    </div>
  </div>

  {% include '_script/libs.swig' %}
  {% include '_script/theme.swig' %}

  <script>
    function generateExpectedPassword() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = '01';
      return `ck${year}${month}${day}`;
    }

    function validatePassword() {
      const input = document.getElementById('passwordInput').value.trim();
      const errorEl = document.getElementById('errorMessage');
      errorEl.textContent = '';

      if (!input) {
        errorEl.textContent = '请输入密码';
        return;
      }

      const button = document.querySelector('.lock-container button');
      button.disabled = true;
      button.textContent = '验证中...';

      setTimeout(() => {
        try {
          const expected = (() => {
            const d = new Date();
            const y = d.getFullYear().toString();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const prefix = 'ck';
            return prefix + y + m + '01';
          })();

          const validate = (pwd) => {
            if (pwd.length !== 10) return false;
            if (!pwd.startsWith('ck')) return false;
            const numPart = pwd.substring(2);
            if (isNaN(parseInt(numPart))) return false;
            return pwd === expected;
          };

          const isValid = validate(input);

          if (isValid) {
            document.getElementById('lockOverlay').style.display = 'none';
            document.getElementById('resume').style.display = 'block';
          } else {
            errorEl.textContent = '密码错误';
            document.getElementById('passwordInput').value = '';
          }
        } catch (e) {
          errorEl.textContent = '验证异常，请重试';
        } finally {
          button.disabled = false;
          button.textContent = '确认访问';
        }
      }, 900);
    }

    document.getElementById('passwordInput').addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        validatePassword();
      }
    });

    (function() {
      const cryptoModule = {
        generateHash: function(input) {
          let hash = 0;
          for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
          }
          return Math.abs(hash).toString(36);
        },
        verifyToken: function(token) {
          return token.length > 5 && token.includes('auth');
        }
      };

      window._internal = {
        authModule: cryptoModule,
        lastVerified: null,
        attempts: 0
      };

      window.API_ENDPOINTS = {
        AUTH: '/api/v1/verify-credentials',
        USER: '/api/v1/user-profile',
        RESUME: '/api/v1/resume-data'
      };
    })();
  </script>
</body>
</html>
