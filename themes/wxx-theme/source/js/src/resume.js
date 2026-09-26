(function () {
  'use strict';
  // Preserve the existing monthly access gate and cache across both languages.
  var form = document.getElementById('resume-access-form');
  var input = document.getElementById('passwordInput');
  var tracker = document.getElementById('resume-analytics');
  var pending = [];
  var recorded = {};
  var sending = false;
  var language = document.body.dataset.resumeLanguage === 'en' ? 'en' : 'zh';
  // Queue early views until the async tracker loads. Serialize requests so the
  // first response establishes the visitor session before subsequent views.
  function flush() {
    if (sending || !pending.length || !window.umami || !window.umami.track) return;
    sending = true;
    var view = pending.shift();
    Promise.resolve().then(function () {
      return window.umami.track(function (props) {
        return Object.assign({}, props, {
          url: '/resume-stats/' + view.stage,
          title: 'Resume ' + view.stage,
          referrer: '',
          tag: 'resume:' + language + (view.auth ? ':' + view.auth : '')
        });
      });
    }).catch(function () {
      // Analytics failures must never interrupt access to the resume.
    }).then(function () { sending = false; flush(); });
  }
  function record(stage, auth) {
    if (!tracker || recorded[stage]) return;
    recorded[stage] = true;
    pending.push({ stage: stage, auth: auth });
    flush();
  }
  if (tracker) tracker.addEventListener('load', flush);
  record('entry');
  function month() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }
  function reveal(focus, auth) {
    document.getElementById('passwordPage').hidden = true;
    document.getElementById('resumePage').hidden = false;
    record('content', auth);
    if (focus) document.querySelector('.resume-name').focus();
  }
  try { if (localStorage.getItem('resume_auth') === month()) reveal(false, 'cached'); } catch (_) {}
  if (!document.getElementById('passwordPage').hidden) record('locked');
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (input.value.trim() === 'ck' + month().replace('-', '') + '01') {
      try { localStorage.setItem('resume_auth', month()); } catch (_) {}
      reveal(true, 'password');
    } else {
      document.getElementById('errorMessage').textContent = document.body.dataset.resumeLanguage === 'en' ? 'Incorrect password. Please try again.' : '密码不正确，请重试。';
      input.value = ''; input.focus();
    }
  });
  document.getElementById('print-resume').addEventListener('click', function () { window.print(); });
  document.querySelectorAll('.resume-container li').forEach(function (li) {
    var match = li.textContent.match(/^【([^】]+)】(.*)$/s);
    if (!match) return;
    var strong = document.createElement('strong');
    strong.textContent = match[1] + ' · ';
    li.replaceChildren(strong, document.createTextNode(match[2]));
  });
}());
