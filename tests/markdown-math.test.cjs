'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Marked } = require('marked');
const { extensions } = require('../lib/markdown-math');
const parse = text => new Marked({ extensions }).parse(text);
test('Math survives Markdown underscores, row separators and HTML-like operators', () => {
  const tex = String.raw`$ W_{in} = \begin{bmatrix} x_1 & x_2 \\ y_1 & y_2 \end{bmatrix}, x < y $`;
  const html = parse(tex);
  assert.ok(html.includes(String.raw`W_{in}`));
  assert.ok(html.includes(String.raw`\\ y_1`));
  assert.ok(html.includes('x &lt; y'));
  assert.ok(!html.includes('<em>'));
});
test('Display delimiters and legacy multiline single-dollar formulas are blocks', () => {
  for (const text of ['$$\nx_1 + x_2\n$$', String.raw`\[x_1\]`, '$ h_1 = x_1 \\\\\nh_2 = x_2 $']) {
    assert.ok(parse(text).includes('class="math-display"'));
  }
});
test('Fenced code, inline code, escaped dollars and currency remain ordinary text', () => {
  for (const text of ['```js\nconst x = "$ a_b $";\n```', '`$ a_b $`', String.raw`\$12 and \$15`, '$12 and $15']) {
    assert.ok(!parse(text).includes('class="math-'));
  }
});
test('Inline math works inside lists and tables, without swallowing following paragraphs', () => {
  const html = parse('- Value: $ x_1 $\n\n| Equation |\n| --- |\n| $y_2$ |\n\nA $5 price.\n\nNext $x$ paragraph.');
  assert.equal((html.match(/class="math-inline"/g) || []).length, 3);
  assert.ok(html.includes('A $5 price.'));
});
