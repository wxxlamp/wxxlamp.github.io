(function () {
  'use strict';
  // Preserve the existing monthly access gate and cache across both languages.
  var form = document.getElementById('resume-access-form');
  var input = document.getElementById('passwordInput');
  function month() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }
  function reveal(focus) {
    document.getElementById('passwordPage').hidden = true;
    document.getElementById('resumePage').hidden = false;
    if (focus) document.querySelector('.resume-name').focus();
  }
  try { if (localStorage.getItem('resume_auth') === month()) reveal(false); } catch (_) {}
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (input.value.trim() === 'ck' + month().replace('-', '') + '01') {
      try { localStorage.setItem('resume_auth', month()); } catch (_) {}
      reveal(true);
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
