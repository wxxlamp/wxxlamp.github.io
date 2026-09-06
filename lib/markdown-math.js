'use strict';

const escapeHtml = text => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
function formula(source, block = false) {
  const opener = ['$$', '\\[', '\\(', '$'].find(mark => source.startsWith(mark));
  if (!opener) return;
  const closer = { '$$': '$$', '\\[': '\\]', '\\(': '\\)', '$': '$' }[opener];
  let end = opener.length;
  while ((end = source.indexOf(closer, end)) !== -1) {
    let slashes = 0;
    for (let i = end - 1; i >= 0 && source[i] === '\\'; i--) slashes++;
    if (slashes % 2 === 0) break;
    end += closer.length;
  }
  if (end < 0) return;
  const text = source.slice(opener.length, end).trim();
  if (!text || /\n\s*\n/.test(text)) return;
  // Do not interpret normal currency ranges as mathematics.
  if (opener === '$' && /^\d[\d,.]*(?:\s+[\p{L}\s]+)?$/u.test(text)) return;
  const display = opener === '$$' || opener === '\\[' || (opener === '$' && text.includes('\n'));
  if (block && !display) return;
  if (!block && text.includes('\n') && !display) return;
  return { raw: source.slice(0, end + closer.length), text, display };
}
function render(token) {
  const tag = token.display ? 'div' : 'span';
  const delimiters = token.display ? ['\\[', '\\]'] : ['\\(', '\\)'];
  return `<${tag} class="math-${token.display ? 'display' : 'inline'}">${delimiters[0]}${escapeHtml(token.text)}${delimiters[1]}</${tag}>`;
}
const extensions = [
  { name: 'blockMath', level: 'block', start: src => src.search(/(?:^|\n)(?:\$\$|\\\[|\$[^\n]*\n)/),
    tokenizer(src) { const token = formula(src, true); if (token) return { type: 'blockMath', ...token }; }, renderer: render },
  { name: 'inlineMath', level: 'inline', start: src => src.search(/\$|\\[([]/),
    tokenizer(src) { const token = formula(src); if (token) return { type: 'inlineMath', ...token }; }, renderer: render }
];
module.exports = { extensions, formula, render };
