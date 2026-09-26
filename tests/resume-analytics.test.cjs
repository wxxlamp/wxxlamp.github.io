const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../themes/wxx-theme/source/js/src/resume.js'), 'utf8');

function setup({ cached = false, language = 'zh', delayed = false, enabled = true, storageError = false, fail = false } = {}) {
  const elements = {};
  for (const id of ['resume-access-form', 'passwordInput', 'passwordPage', 'resumePage', 'errorMessage', 'print-resume', 'resume-analytics']) {
    elements[id] = { hidden: id === 'resumePage', value: '', handlers: {},
      addEventListener(event, handler) { this.handlers[event] = handler; }, focus() {} };
  }
  if (!enabled) delete elements['resume-analytics'];
  const views = [];
  const now = new Date();
  const month = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
  const window = { print() {} };
  function load() {
    window.umami = { track(callback) {
      if (fail) return Promise.reject(new Error('offline'));
      views.push(callback({ website: 'self', url: '/resume/?sensitive=1', title: 'Private name', referrer: 'https://example.com/?secret=1' }));
      return Promise.resolve();
    } };
    if (elements['resume-analytics']) elements['resume-analytics'].handlers.load?.();
  }
  if (!delayed) load();
  vm.runInNewContext(source, {
    window, Date, Promise,
    localStorage: {
      getItem() { if (storageError) throw new Error('blocked'); return cached ? month : null; },
      setItem() { if (storageError) throw new Error('blocked'); }
    },
    document: {
      body: { dataset: { resumeLanguage: language } },
      getElementById(id) { return elements[id]; },
      querySelector() { return { focus() {} }; }, querySelectorAll() { return []; }
    }
  });
  return { views, elements, load, submit(correct = true) {
    elements.passwordInput.value = correct ? 'ck' + month.replace('-', '') + '01' : 'wrong';
    elements['resume-access-form'].handlers.submit({ preventDefault() {} });
  } };
}
const settle = () => new Promise(resolve => setImmediate(resolve));
const stages = app => app.views.map(view => view.url);

test('Delayed tracker preserves entry/locked/content order; wrong passwords and repeated submits add no views', async () => {
  const app = setup({ delayed: true });
  app.submit(false);
  assert.equal(app.elements.resumePage.hidden, true);
  app.submit(); app.submit();
  assert.equal(app.elements.resumePage.hidden, false);
  assert.equal(app.views.length, 0);
  app.load(); await settle();
  assert.deepEqual(stages(app), ['/resume-stats/entry', '/resume-stats/locked', '/resume-stats/content']);
  assert.equal(app.views[2].tag, 'resume:zh:password');
  for (const view of app.views) {
    assert.equal(view.referrer, '');
    assert.equal(view.website, 'self');
    assert.doesNotMatch(JSON.stringify(view), /sensitive|secret|Private name|wrong/);
  }
});

test('Cached authorization records entry and content in both languages, with no locked view', async () => {
  for (const language of ['zh', 'en']) {
    const app = setup({ cached: true, language });
    await settle();
    assert.deepEqual(stages(app), ['/resume-stats/entry', '/resume-stats/content']);
    assert.equal(app.views[1].tag, 'resume:' + language + ':cached');
  }
});

test('Fresh page loads count again while disabled analytics, storage errors and tracker failures preserve access', async () => {
  for (const options of [{}, { storageError: true }, { enabled: false }, { fail: true }]) {
    for (let visit = 0; visit < 2; visit++) {
      const app = setup(options);
      app.submit(); await settle();
      assert.equal(app.elements.resumePage.hidden, false);
      assert.equal(app.views.length, options.enabled === false || options.fail ? 0 : 3);
    }
  }
});
