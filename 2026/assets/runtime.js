/*
 * Minimal stand-alone runtime for the THE RACE 2026 dashboard page.
 * It provides the small `dash` API the page code expects (data, calc,
 * onData, params, colors, setLink) and loads the weekly data files
 * from ./data/ so the same page runs on any static host. League history
 * files (../history/data/) load on first use.
 */
(function () {
  'use strict';

  const VERSION = (document.querySelector('meta[name="data-version"]') || {}).content || '';
  const DATASETS = {
    hebdo: 'data/hebdo.json',
    joueurs: 'data/joueurs.json',
    players: 'data/players.json',
    matches: 'data/matches.json',
    calendar: 'data/calendar.json',
    team_colors: 'data/team_colors.json',
  };
  // League history (2019 onwards), loaded only when a page first asks for it (Historique tab).
  const LAZY = {
    hist_seasons: '../history/data/seasons.json',
    hist_hebdo: '../history/data/hebdo.json',
    hist_rosters: '../history/data/rosters.json',
    hist_players: '../history/data/players.json',
    hist_ranks: '../history/data/ranks.json',
    hist_calendar: '../history/data/calendar.json',
  };
  const DEFAULT_PARAMS = { player: null, team: 'All' };

  const state = {};        // id -> {status, data, message}
  const calcs = {};        // id -> {inputs, fn}
  const calcCache = {};    // id -> {key, result}
  const listeners = [];
  let params = Object.assign({}, DEFAULT_PARAMS);

  const rowsOf = (json) => {
    if (Array.isArray(json)) return json;
    if (json && typeof json === 'object') {
      for (const k of ['rows', 'data', 'results']) if (Array.isArray(json[k])) return json[k];
    }
    return json;
  };

  const has = (o, id) => Object.prototype.hasOwnProperty.call(o, id);
  const isDataset = (id) => has(DATASETS, id) || has(LAZY, id);
  const load = (id, url) => {
    state[id] = { status: 'loading', data: [] };
    fetch(url + (VERSION ? '?v=' + encodeURIComponent(VERSION) : ''), { cache: 'no-cache' })
      .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then((json) => { state[id] = { status: 'ok', data: rowsOf(json) }; notify(); })
      .catch((err) => { console.error('[race] could not load', url, err); state[id] = { status: 'error', data: [], message: String(err) }; notify(); });
  };

  function datasetResult(id) {
    if (!state[id] && has(LAZY, id)) load(id, LAZY[id]);
    const s = state[id];
    if (!s) return { status: 'loading', data: [], columns: [], message: '', refreshing: false, meta: [] };
    const data = s.data || [];
    const columns = Array.isArray(data) && data.length && typeof data[0] === 'object' ? Object.keys(data[0]) : [];
    return { status: s.status, data, rows: data, columns, message: s.message || '', refreshing: false, meta: [] };
  }

  function calcResult(id) {
    const c = calcs[id];
    const inputs = c.inputs.map((i) => api.data(i));
    if (inputs.some((r) => r.status === 'error')) return { status: 'error', data: [], columns: [], message: 'Une source n’a pas pu être chargée.', refreshing: false, meta: [] };
    if (inputs.some((r) => r.status !== 'ok')) return { status: 'loading', data: [], columns: [], message: '', refreshing: false, meta: [] };
    const key = inputs.map((r) => r.data);
    const cached = calcCache[id];
    if (cached && cached.key.length === key.length && cached.key.every((d, i) => d === key[i])) return cached.result;
    let result;
    try {
      const out = c.fn(...key);
      const columns = Array.isArray(out) && out.length && typeof out[0] === 'object' ? Object.keys(out[0]) : [];
      result = { status: 'ok', data: out, rows: out, columns, message: '', refreshing: false, meta: [] };
    } catch (err) {
      console.error('[race] calc failed:', id, err);
      result = { status: 'error', data: [], columns: [], message: String(err), refreshing: false, meta: [] };
    }
    calcCache[id] = { key, result };
    return result;
  }

  let scheduled = false;
  function notify() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      listeners.forEach((fn) => {
        try { fn(); } catch (err) { console.error('[race] render failed:', err); }
      });
    });
  }

  const api = {
    colors: ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948'],
    data(id) {
      if (isDataset(id)) return datasetResult(id);
      if (calcs[id]) return calcResult(id);
      return { status: 'missing', data: [], columns: [], message: 'Source inconnue : ' + id, refreshing: false, meta: [] };
    },
    calc(id, def) {
      calcs[id] = { inputs: def.inputs || [], fn: def.fn };
    },
    loader() { /* not used on this site */ },
    onData(fn) {
      listeners.push(fn);
      try { fn(); } catch (err) { console.error('[race] render failed:', err); }
    },
    params() { return Object.assign({}, params); },
    setParams(next) { params = Object.assign({}, params, next); notify(); },
    resetParams() { params = Object.assign({}, DEFAULT_PARAMS); notify(); },
    setLink(name) {
      try { history.replaceState(null, '', name ? '#' + name : location.pathname + location.search); } catch (e) { /* ignore */ }
    },
    refresh() { /* data is a weekly snapshot */ },
  };
  window.dash = api;

  // Load every data file once.
  Object.entries(DATASETS).forEach(([id, url]) => load(id, url));

  // Redraw when the available width changes (phone rotation, window resize).
  let lastWidth = 0;
  let resizeTimer = null;
  const root = () => document.getElementById('dash-root');
  const watchWidth = () => {
    const el = root();
    if (!el) return;
    const w = el.clientWidth;
    if (w !== lastWidth) { lastWidth = w; notify(); }
  };
  window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(watchWidth, 120); });
  document.addEventListener('DOMContentLoaded', () => { const el = root(); if (el) lastWidth = el.clientWidth; });
})();
