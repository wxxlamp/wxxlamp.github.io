(function (root) {
  'use strict';
  function normalize(text) { return String(text || '').normalize('NFKC').toLowerCase(); }
  // One insertion, deletion, substitution or adjacent transposition for English words.
  function near(a, b) {
    if (Math.abs(a.length - b.length) > 1) return false;
    if (a === b) return true;
    for (var i = 0; i < Math.min(a.length, b.length); i++) {
      if (a[i] === b[i]) continue;
      if (a.length === b.length) return a.slice(i + 1) === b.slice(i + 1) ||
        (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2));
      return a.length > b.length ? a.slice(i + 1) === b.slice(i) : a.slice(i) === b.slice(i + 1);
    }
    return true;
  }
  function prepare(entries) {
    return entries.map(function (entry) {
      return { entry: entry, fields: [entry.title, (entry.categories || []).join(' '), (entry.tags || []).join(' '), entry.description, entry.body].map(normalize) };
    });
  }
  function search(records, query, filters) {
    filters = filters || {};
    var terms = normalize(query).trim().split(/\s+/).filter(Boolean).slice(0, 12);
    if (!terms.length && !filters.category && !filters.tag && !filters.kind) return [];
    return records.map(function (record) {
      var entry = record.entry;
      if (filters.kind && entry.kind !== filters.kind || filters.category && !entry.categories.includes(filters.category) || filters.tag && !entry.tags.includes(filters.tag)) return null;
      var score = 0;
      for (var term of terms) {
        var best = 0;
        record.fields.forEach(function (field, index) {
          var weight = [12, 9, 9, 4, 1][index];
          if (field.includes(term)) best = Math.max(best, weight * (field === term ? 2 : 1));
          else if (/^[a-z]{4,}$/.test(term) && field.split(/[^a-z]+/).some(function (word) { return near(term, word); })) best = Math.max(best, weight * .4);
        });
        if (!best) return null;
        score += best;
      }
      return { entry: entry, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score || a.entry.title.localeCompare(b.entry.title); });
  }
  var api = { prepare: prepare, search: search, normalize: normalize };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SiteSearch = api;
})(typeof window === 'object' ? window : globalThis);
