/* =========================================================
   MedicoAI – SPA Application Logic
   Hash-based routing: #/ | #/especialidade/:slug |
   #/hospital/:slug | #/medico/:id | #/busca | #/chat
   #/especialidades | #/hospitais
   ========================================================= */

'use strict';

// ─── API Base ────────────────────────────────────────────
const API = '/api';

// ─── Avatar Color Palette ────────────────────────────────
const AVATAR_COLORS = [
  '#2b6cb0','#276749','#9b2c2c','#6b46c1','#c05621',
  '#2c7a7b','#822727','#285e61','#44337a','#1a365d',
];

function avatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function initials(name) {
  const parts = (name || '').trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

// ─── SVG Icons ───────────────────────────────────────────
const ICONS = {
  search: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>`,
  chevronRight: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>`,
  chevronLeft: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>`,
  hospital: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>`,
  mapPin: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  clock: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  dollar: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
  award: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>`,
  users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  star: `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`,
  sticker: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.47-1.125"/><path d="M20.8 11C20.26 7.14 16.81 4 12.6 4c-4.67 0-8.6 3.54-9 8.14-.02.226-.03.453-.03.68 0 2.86 1.95 5.25 4.54 5.96"/><path d="M18 16.24V16a2 2 0 1 1 2 2h-.24"/><path d="M13.83 19.17a4.5 4.5 0 0 0 4.58 2.8"/></svg>`,
  chat: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  send: `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`,
  clipboard: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>`,
  heart: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>`,
  calendar: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
};

// ─── Specialty Icons & Colors ────────────────────────────
const SPECIALTY_CONFIG = {
  cardiologia:       { bg: '#fff5f5', color: '#e53e3e', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>` },
  neurologia:        { bg: '#f5f0ff', color: '#805ad5', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>` },
  ortopedia:         { bg: '#fff8f0', color: '#dd6b20', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>` },
  dermatologia:      { bg: '#f0fff4', color: '#38a169', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>` },
  pediatria:         { bg: '#ebf8ff', color: '#3182ce', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>` },
  ginecologia:       { bg: '#fff5f7', color: '#d53f8c', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M12 12v9"/><path d="M9 18h6"/></svg>` },
  oftalmologia:      { bg: '#e6fffa', color: '#2c7a7b', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>` },
  urologia:          { bg: '#fffff0', color: '#b7791f', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22V12"/><path d="m4.93 4.93 4.24 4.24"/><path d="M2 12h4"/><path d="M19.07 4.93l-4.24 4.24"/><path d="M22 12h-4"/><path d="M12 2v4"/></svg>` },
  default:           { bg: '#ebf8ff', color: '#3182ce', icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>` },
};

function getSpecialtyConfig(name) {
  const key = (name || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  return SPECIALTY_CONFIG[key] || SPECIALTY_CONFIG.default;
}

// ─── Stars Renderer ──────────────────────────────────────
function renderStars(rating, size = 16) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  const starSVG = (fill) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${fill}" xmlns="http://www.w3.org/2000/svg"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`;
  let html = '';
  for (let i = 0; i < full; i++) html += `<span class="star-filled">${starSVG('#f6ad55')}</span>`;
  if (half) html += `<span class="star-half">${starSVG('#f6ad55')}</span>`;
  for (let i = 0; i < empty; i++) html += `<span class="star-empty">${starSVG('#e2e8f0')}</span>`;
  return `<div class="stars-display">${html}</div>`;
}

// ─── Breadcrumb Helper ───────────────────────────────────
function breadcrumb(items) {
  const sep = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>`;
  return `<nav class="breadcrumbs" aria-label="Breadcrumb">${items.map((item, i) => {
    if (i === items.length - 1) return `<span>${item.label}</span>`;
    return `<a href="${item.href}">${item.label}</a>${sep}`;
  }).join('')}</nav>`;
}

// ─── Skeleton Cards ──────────────────────────────────────
function skeletonCards(count = 5) {
  return Array.from({ length: count }).map(() => `
    <div class="skeleton-card">
      <div class="skeleton skeleton-avatar"></div>
      <div class="skeleton-lines">
        <div class="skeleton skeleton-line long"></div>
        <div class="skeleton skeleton-line medium"></div>
        <div class="skeleton skeleton-line short"></div>
      </div>
    </div>
  `).join('');
}

// ─── Doctor Card ─────────────────────────────────────────
function doctorCard(doc) {
  const color = avatarColor(doc.nome || '');
  const ini = initials(doc.nome || '');
  const rating = parseFloat(doc.nota_media || 0).toFixed(1);
  const total = doc.total_avaliacoes || 0;
  const hospital = doc.hospital_principal || doc.hospital || '';
  const subesp = doc.subespecialidade || doc.especialidade || '';
  const preco = doc.valor_consulta ? `R$ ${parseFloat(doc.valor_consulta).toFixed(0)}` : null;

  return `
    <a class="doctor-card page-enter" href="#/medico/${doc.id}" role="article">
      <div class="doctor-avatar" style="background:${color}" aria-hidden="true">${ini}</div>
      <div class="doctor-info">
        <div class="doctor-name">${escHtml(doc.nome || 'Médico')}</div>
        <div class="doctor-specialty-tag">${escHtml(subesp)}</div>
        <div class="doctor-meta">
          ${hospital ? `<span class="doctor-meta-item">${ICONS.mapPin}${escHtml(hospital)}</span>` : ''}
          ${doc.anos_experiencia ? `<span class="doctor-meta-item">${ICONS.clock}${doc.anos_experiencia} anos</span>` : ''}
        </div>
      </div>
      <div class="doctor-right">
        <div class="doctor-rating">
          ${renderStars(parseFloat(rating))}
          <span class="rating-value">${rating}</span>
          <span class="rating-count">(${total})</span>
        </div>
        ${preco ? `<div><div class="doctor-price">${preco}</div><div class="doctor-price-label">consulta</div></div>` : ''}
      </div>
    </a>
  `;
}

// ─── HTML Escape ─────────────────────────────────────────
function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── Markdown-lite formatter (for chat) ──────────────────
function formatMarkdown(text) {
  if (!text) return '';
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/((?:^|\n)[•\-] .+)+/g, (match) => {
    const items = match.trim().split('\n')
      .map(l => l.replace(/^[•\-]\s/, '').trim())
      .filter(Boolean)
      .map(i => `<li>${i}</li>`).join('');
    return `<ul>${items}</ul>`;
  });
  html = html.replace(/\n/g, '<br>');
  html = html.replace(/<br>\s*(<\/?ul>|<\/?li>)/g, '$1');
  html = html.replace(/(<\/?ul>|<\/?li>)\s*<br>/g, '$1');
  return html;
}

// ─── API Fetch Helper ────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

// ─── Pagination ──────────────────────────────────────────
function renderPagination(currentPage, totalPages, onNavigate) {
  if (totalPages <= 1) return '';
  const pages = [];
  let start = Math.max(1, currentPage - 2);
  let end = Math.min(totalPages, currentPage + 2);
  if (end - start < 4) {
    if (start === 1) end = Math.min(totalPages, start + 4);
    else start = Math.max(1, end - 4);
  }

  const btn = (label, page, active = false, disabled = false) =>
    `<button class="page-btn${active ? ' active' : ''}" data-page="${page}" ${disabled ? 'disabled' : ''}>${label}</button>`;

  pages.push(btn(ICONS.chevronLeft, currentPage - 1, false, currentPage === 1));
  if (start > 1) { pages.push(btn('1', 1)); if (start > 2) pages.push(`<span style="padding:0 4px;color:var(--gray-400)">…</span>`); }
  for (let p = start; p <= end; p++) pages.push(btn(p, p, p === currentPage));
  if (end < totalPages) { if (end < totalPages - 1) pages.push(`<span style="padding:0 4px;color:var(--gray-400)">…</span>`); pages.push(btn(totalPages, totalPages)); }
  pages.push(btn(ICONS.chevronRight, currentPage + 1, false, currentPage === totalPages));

  const container = document.createElement('div');
  container.className = 'pagination';
  container.innerHTML = pages.join('');
  container.querySelectorAll('button:not([disabled])').forEach(b => {
    b.addEventListener('click', () => onNavigate(parseInt(b.dataset.page)));
  });
  return container;
}

// =========================================================
//   PAGES
// =========================================================

// ─── HOME PAGE ───────────────────────────────────────────
async function renderHome(app) {
  app.innerHTML = `
    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner page-enter">
        <div class="hero-eyebrow">
          ${ICONS.heart}
          Porto Alegre · Rio Grande do Sul
        </div>
        <h1>Encontre médicos de <span>confiança</span> em Porto Alegre</h1>
        <p class="hero-sub">Acesse perfis completos, avaliações de pacientes e informações sobre especialistas da sua cidade.</p>
        <div class="hero-search-bar" id="hero-search-bar">
          ${ICONS.search}
          <input type="text" id="hero-search-input" placeholder="Buscar por médico, especialidade ou hospital..." autocomplete="off" />
          <button class="hero-search-btn" id="hero-search-btn">
            ${ICONS.search}
            Buscar
          </button>
        </div>
      </div>
    </section>

    <!-- Stats Bar -->
    <div class="stats-bar" id="stats-bar">
      <div class="stats-bar-inner" id="stats-inner">
        <div class="stat-item">
          <div class="stat-icon">${ICONS.users}</div>
          <div class="stat-text">
            <span class="stat-value" id="stat-medicos">—</span>
            <span class="stat-label">Médicos cadastrados</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">${ICONS.star}</div>
          <div class="stat-text">
            <span class="stat-value" id="stat-avaliacoes">—</span>
            <span class="stat-label">Avaliações</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">${ICONS.clipboard}</div>
          <div class="stat-text">
            <span class="stat-value" id="stat-especialidades">—</span>
            <span class="stat-label">Especialidades</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Especialidades -->
    <div class="home-section">
      <div class="section-header">
        <div>
          <div class="section-title">Especialidades</div>
          <div class="section-subtitle">Encontre médicos por área de atuação</div>
        </div>
        <a href="#/especialidades" class="section-link">Ver todas ${ICONS.chevronRight}</a>
      </div>
      <div class="specialties-grid" id="home-specialties">
        ${skeletonCards(8).replace(/skeleton-card/g, 'specialty-card').replace(/skeleton-avatar|skeleton-lines|skeleton-line [a-z]+/g, 'skeleton')}
      </div>
    </div>

    <!-- Hospitais -->
    <div class="home-section" style="padding-top:0">
      <div class="section-header">
        <div>
          <div class="section-title">Hospitais</div>
          <div class="section-subtitle">Principais hospitais e clínicas de Porto Alegre</div>
        </div>
        <a href="#/hospitais" class="section-link">Ver todos ${ICONS.chevronRight}</a>
      </div>
      <div class="hospitals-grid" id="home-hospitals">
        ${skeletonCards(6).replace(/skeleton-card/g, 'hospital-card').replace(/skeleton-avatar|skeleton-lines|skeleton-line [a-z]+/g, 'skeleton')}
      </div>
    </div>
  `;

  // Hero search
  const heroInput = document.getElementById('hero-search-input');
  const heroBtn = document.getElementById('hero-search-btn');
  const doSearch = () => {
    const q = (heroInput.value || '').trim();
    if (q) navigate(`/busca?q=${encodeURIComponent(q)}`);
  };
  heroBtn.addEventListener('click', doSearch);
  heroInput.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });

  // Load stats
  apiFetch('/stats').then(data => {
    const m = document.getElementById('stat-medicos');
    const a = document.getElementById('stat-avaliacoes');
    const e = document.getElementById('stat-especialidades');
    if (m) m.textContent = (data.total_medicos || '—').toLocaleString('pt-BR');
    if (a) a.textContent = (data.total_avaliacoes || '—').toLocaleString('pt-BR');
    if (e) e.textContent = (data.total_especialidades || '—').toLocaleString('pt-BR');
  }).catch(() => {});

  // Load specialties
  apiFetch('/especialidades').then(list => {
    const grid = document.getElementById('home-specialties');
    if (!grid) return;
    const shown = list.slice(0, 12);
    grid.innerHTML = shown.map(item => {
      const cfg = getSpecialtyConfig(item.especialidade);
      return `
        <a class="specialty-card page-enter" href="#/especialidade/${encodeURIComponent(item.slug || item.especialidade)}">
          <div class="specialty-icon" style="background:${cfg.bg};color:${cfg.color}">${cfg.icon}</div>
          <div class="specialty-name">${escHtml(item.especialidade)}</div>
          <div class="specialty-count">${item.count || 0} médico${item.count !== 1 ? 's' : ''}</div>
        </a>
      `;
    }).join('');
  }).catch(() => {
    const grid = document.getElementById('home-specialties');
    if (grid) grid.innerHTML = `<div class="text-muted" style="grid-column:1/-1">Erro ao carregar especialidades.</div>`;
  });

  // Load hospitals
  apiFetch('/hospitais').then(list => {
    const grid = document.getElementById('home-hospitals');
    if (!grid) return;
    const shown = list.slice(0, 8);
    grid.innerHTML = shown.map(item => `
      <a class="hospital-card page-enter" href="#/hospital/${encodeURIComponent(item.slug || item.hospital)}">
        <div class="hospital-icon">${ICONS.hospital}</div>
        <div>
          <div class="hospital-name">${escHtml(item.hospital)}</div>
          <div class="hospital-count">${item.count || 0} médico${item.count !== 1 ? 's' : ''}</div>
        </div>
      </a>
    `).join('');
  }).catch(() => {
    const grid = document.getElementById('home-hospitals');
    if (grid) grid.innerHTML = `<div class="text-muted" style="grid-column:1/-1">Erro ao carregar hospitais.</div>`;
  });
}

// ─── SPECIALTY / HOSPITAL / SEARCH LIST PAGE ─────────────
async function renderList(app, { type, slug, query, title, apiPath, breadcrumbs }) {
  const PER_PAGE = 20;
  let allDoctors = [];
  let currentPage = 1;
  let sortBy = 'nota';
  let pageTitle = title || 'Médicos';
  let pageSubtitle = '';

  app.innerHTML = `
    <div class="inner-page-hero">
      <div class="inner-page-hero-inner page-enter">
        <div id="list-bc"></div>
        <h1 id="list-title">${escHtml(pageTitle)}</h1>
        <p id="list-subtitle" class="hero-sub" style="margin:0;font-size:14px;opacity:0.8"></p>
      </div>
    </div>
    <div class="list-page">
      <div class="list-controls">
        <span class="results-count" id="results-count">Carregando...</span>
        <select class="sort-select" id="sort-select">
          <option value="nota">Ordenar por: Melhor nota</option>
          <option value="avaliacoes">Mais avaliados</option>
          <option value="experiencia">Mais experientes</option>
        </select>
      </div>
      <div id="doctors-container">${skeletonCards(6)}</div>
      <div id="pagination-container"></div>
    </div>
  `;

  // Breadcrumbs
  const bc = document.getElementById('list-bc');
  if (bc && breadcrumbs) bc.innerHTML = breadcrumbs;

  const sortSelect = document.getElementById('sort-select');
  sortSelect.addEventListener('change', () => {
    sortBy = sortSelect.value;
    currentPage = 1;
    renderCurrentPage();
  });

  function sortedDoctors() {
    const copy = [...allDoctors];
    if (sortBy === 'nota') return copy.sort((a, b) => (parseFloat(b.nota_media) || 0) - (parseFloat(a.nota_media) || 0));
    if (sortBy === 'avaliacoes') return copy.sort((a, b) => (parseInt(b.total_avaliacoes) || 0) - (parseInt(a.total_avaliacoes) || 0));
    if (sortBy === 'experiencia') return copy.sort((a, b) => (parseInt(b.anos_experiencia) || 0) - (parseInt(a.anos_experiencia) || 0));
    return copy;
  }

  function renderCurrentPage() {
    const container = document.getElementById('doctors-container');
    const pagContainer = document.getElementById('pagination-container');
    const countEl = document.getElementById('results-count');
    if (!container) return;

    const sorted = sortedDoctors();
    const totalPages = Math.ceil(sorted.length / PER_PAGE);
    const slice = sorted.slice((currentPage - 1) * PER_PAGE, currentPage * PER_PAGE);

    if (countEl) countEl.textContent = `${sorted.length} médico${sorted.length !== 1 ? 's' : ''} encontrado${sorted.length !== 1 ? 's' : ''}`;

    if (slice.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">${ICONS.search}</div>
          <div class="empty-state-title">Nenhum médico encontrado</div>
          <div class="empty-state-text">Tente uma busca diferente ou explore outras especialidades.</div>
        </div>`;
      if (pagContainer) pagContainer.innerHTML = '';
      return;
    }

    container.innerHTML = `<div class="doctors-list">${slice.map(doctorCard).join('')}</div>`;

    if (pagContainer) {
      pagContainer.innerHTML = '';
      const pag = renderPagination(currentPage, totalPages, (p) => {
        currentPage = p;
        renderCurrentPage();
        document.querySelector('.list-page')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      if (typeof pag !== 'string') pagContainer.appendChild(pag);
    }
  }

  // Fetch data
  try {
    const data = await apiFetch(apiPath);
    if (data.medicos) allDoctors = data.medicos;
    else if (Array.isArray(data)) allDoctors = data;

    const titleEl = document.getElementById('list-title');
    const subEl = document.getElementById('list-subtitle');
    if (titleEl && (data.especialidade || data.hospital || data.query)) {
      titleEl.textContent = data.especialidade || data.hospital || `Busca: "${data.query}"`;
    }
    if (subEl) subEl.textContent = `${allDoctors.length} médico${allDoctors.length !== 1 ? 's' : ''} encontrado${allDoctors.length !== 1 ? 's' : ''}`;

    renderCurrentPage();
  } catch (err) {
    const container = document.getElementById('doctors-container');
    if (container) container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">${ICONS.search}</div><div class="empty-state-title">Erro ao carregar</div><div class="empty-state-text">Não foi possível carregar os médicos. Tente novamente.</div></div>`;
    console.error('[MedicoAI] List load error:', err);
  }
}

// ─── DOCTOR PROFILE PAGE ─────────────────────────────────
async function renderProfile(app, id) {
  app.innerHTML = `
    <div class="profile-page">
      ${breadcrumb([{label:'Início',href:'#/'},{label:'Carregando...'}])}
      <div id="profile-content">${skeletonCards(4)}</div>
    </div>
  `;

  try {
    const doc = await apiFetch(`/medicos/${encodeURIComponent(id)}`);
    const color = avatarColor(doc.nome || '');
    const ini = initials(doc.nome || '');
    const rating = parseFloat(doc.nota_media || 0);
    const ratingStr = rating.toFixed(1);

    // Breadcrumb update
    const bcEl = app.querySelector('.breadcrumbs');
    if (bcEl) {
      const espSlug = doc.slug_especialidade || encodeURIComponent(doc.especialidade || '');
      bcEl.outerHTML = breadcrumb([
        {label:'Início',href:'#/'},
        {label: doc.especialidade || 'Especialidade', href:`#/especialidade/${espSlug}`},
        {label: doc.nome || 'Médico'},
      ]);
    }

    const convenios = Array.isArray(doc.convenios) ? doc.convenios : (doc.convenios ? [doc.convenios] : []);
    const hospitais = Array.isArray(doc.hospitais) ? doc.hospitais : (doc.hospital_principal ? [doc.hospital_principal] : []);
    const procedimentos = Array.isArray(doc.procedimentos) ? doc.procedimentos : [];
    const avaliacoes = Array.isArray(doc.avaliacoes) ? doc.avaliacoes : [];

    const content = document.getElementById('profile-content');
    content.innerHTML = `
      <!-- Profile Header -->
      <div class="profile-header page-enter">
        <div class="profile-avatar-large" style="background:${color}">${ini}</div>
        <div class="profile-header-info">
          <div class="profile-name">${escHtml(doc.nome || 'Médico')}</div>
          <div class="profile-crm">CRM ${escHtml(doc.crm || '—')} &middot; ${escHtml(doc.uf || 'RS')}</div>
          <div class="profile-specialty-badges">
            ${doc.especialidade ? `<span class="badge badge-blue">${escHtml(doc.especialidade)}</span>` : ''}
            ${doc.subespecialidade ? `<span class="badge badge-gray">${escHtml(doc.subespecialidade)}</span>` : ''}
          </div>
          <div class="profile-rating-row">
            <div class="profile-rating-score">${ratingStr}</div>
            <div class="profile-rating-detail">
              <div class="profile-stars">${renderStars(rating, 18).replace('class="stars-display"','class="profile-stars"')}</div>
              <div class="profile-rating-count">${doc.total_avaliacoes || 0} avaliação${(doc.total_avaliacoes || 0) !== 1 ? 'ões' : ''}</div>
            </div>
          </div>
        </div>
        <div class="profile-header-actions">
          <a href="#/chat?medico=${encodeURIComponent(doc.nome || '')}&id=${id}" class="btn-primary">
            ${ICONS.chat}
            Consultar via IA
          </a>
          <button class="btn-secondary" onclick="history.back()">
            ${ICONS.chevronLeft}
            Voltar
          </button>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="profile-info-grid page-enter">
        ${doc.anos_experiencia ? `
        <div class="info-card">
          <div class="info-card-icon blue">${ICONS.award}</div>
          <div>
            <div class="info-card-label">Experiência</div>
            <div class="info-card-value">${doc.anos_experiencia} anos</div>
          </div>
        </div>` : ''}
        ${doc.valor_consulta ? `
        <div class="info-card">
          <div class="info-card-icon green">${ICONS.dollar}</div>
          <div>
            <div class="info-card-label">Valor da consulta</div>
            <div class="info-card-value">R$ ${parseFloat(doc.valor_consulta).toFixed(0)}</div>
          </div>
        </div>` : ''}
        ${convenios.length > 0 ? `
        <div class="info-card">
          <div class="info-card-icon gold">${ICONS.heart}</div>
          <div>
            <div class="info-card-label">Convênios</div>
            <div class="info-card-value" style="font-size:13px;font-weight:500;color:var(--gray-700)">${convenios.slice(0,3).map(escHtml).join(', ')}${convenios.length > 3 ? ` +${convenios.length-3}` : ''}</div>
          </div>
        </div>` : ''}
        <div class="info-card">
          <div class="info-card-icon navy">${ICONS.star}</div>
          <div>
            <div class="info-card-label">Avaliação média</div>
            <div class="info-card-value">${ratingStr} / 5.0</div>
          </div>
        </div>
      </div>

      ${hospitais.length > 0 ? `
      <!-- Hospitals -->
      <div class="profile-section page-enter">
        <div class="profile-section-title">${ICONS.hospital}Hospitais onde atende</div>
        <div class="profile-hospitals">
          ${hospitais.map(h => `
            <a class="profile-hospital-tag" href="#/hospital/${encodeURIComponent((h.slug || h.nome || h).replace(/\s+/g,'-').toLowerCase())}">
              ${ICONS.hospital}
              ${escHtml(h.nome || h)}
            </a>
          `).join('')}
        </div>
      </div>` : ''}

      ${procedimentos.length > 0 ? `
      <!-- Procedures -->
      <div class="profile-section page-enter">
        <div class="profile-section-title">${ICONS.clipboard}Procedimentos realizados</div>
        <div style="overflow-x:auto">
          <table class="procedures-table">
            <thead>
              <tr>
                <th>Procedimento</th>
                <th>Quantidade</th>
                <th>Ano</th>
              </tr>
            </thead>
            <tbody>
              ${procedimentos.map(p => `
                <tr>
                  <td>${escHtml(p.nome || p.procedimento || '')}</td>
                  <td>${p.quantidade || '—'}</td>
                  <td>${p.ano || '—'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>` : ''}

      ${avaliacoes.length > 0 ? `
      <!-- Reviews -->
      <div class="profile-section page-enter">
        <div class="profile-section-title">${ICONS.star}Avaliações de pacientes</div>
        <div class="reviews-list">
          ${avaliacoes.map(rev => {
            const revRating = parseFloat(rev.nota || 0);
            const revDate = rev.data ? new Date(rev.data).toLocaleDateString('pt-BR', {month:'short',year:'numeric'}) : '';
            return `
              <div class="review-card">
                <div class="review-header">
                  <div class="review-patient">${escHtml(rev.nome_paciente || rev.paciente || 'Paciente anônimo')}</div>
                  ${revDate ? `<div class="review-date">${revDate}</div>` : ''}
                </div>
                <div class="review-stars">${renderStars(revRating, 14)}</div>
                ${rev.aspecto ? `<div class="review-aspect">${ICONS.sticker}${escHtml(rev.aspecto)}</div>` : ''}
                ${rev.comentario ? `<div class="review-text">"${escHtml(rev.comentario)}"</div>` : ''}
              </div>
            `;
          }).join('')}
        </div>
      </div>` : ''}
    `;
  } catch (err) {
    const content = document.getElementById('profile-content');
    if (content) content.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${ICONS.search}</div>
        <div class="empty-state-title">Médico não encontrado</div>
        <div class="empty-state-text">O perfil solicitado não existe ou não está disponível.</div>
        <a href="#/" style="margin-top:20px;display:inline-block" class="btn-primary">Voltar ao início</a>
      </div>`;
    console.error('[MedicoAI] Profile load error:', err);
  }
}

// ─── SPECIALTIES LIST PAGE ───────────────────────────────
async function renderSpecialtiesPage(app) {
  app.innerHTML = `
    <div class="inner-page-hero">
      <div class="inner-page-hero-inner page-enter">
        ${breadcrumb([{label:'Início',href:'#/'},{label:'Especialidades'}])}
        <h1>Especialidades</h1>
        <p style="opacity:0.8;font-size:15px;margin-top:6px">Todas as especialidades médicas disponíveis em Porto Alegre</p>
      </div>
    </div>
    <div class="list-page">
      <div class="full-specialties-grid" id="all-specialties">${skeletonCards(12)}</div>
    </div>
  `;
  try {
    const list = await apiFetch('/especialidades');
    const grid = document.getElementById('all-specialties');
    if (!grid) return;
    grid.innerHTML = list.map(item => {
      const cfg = getSpecialtyConfig(item.especialidade);
      return `
        <a class="specialty-card page-enter" href="#/especialidade/${encodeURIComponent(item.slug || item.especialidade)}">
          <div class="specialty-icon" style="background:${cfg.bg};color:${cfg.color}">${cfg.icon}</div>
          <div class="specialty-name">${escHtml(item.especialidade)}</div>
          <div class="specialty-count">${item.count || 0} médico${item.count !== 1 ? 's' : ''}</div>
        </a>
      `;
    }).join('');
  } catch (err) {
    const grid = document.getElementById('all-specialties');
    if (grid) grid.innerHTML = `<div class="text-muted">Erro ao carregar especialidades.</div>`;
  }
}

// ─── HOSPITALS LIST PAGE ─────────────────────────────────
async function renderHospitalsPage(app) {
  app.innerHTML = `
    <div class="inner-page-hero">
      <div class="inner-page-hero-inner page-enter">
        ${breadcrumb([{label:'Início',href:'#/'},{label:'Hospitais'}])}
        <h1>Hospitais e Clínicas</h1>
        <p style="opacity:0.8;font-size:15px;margin-top:6px">Principais estabelecimentos de saúde em Porto Alegre</p>
      </div>
    </div>
    <div class="list-page">
      <div class="hospitals-grid" id="all-hospitals" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">${skeletonCards(8)}</div>
    </div>
  `;
  try {
    const list = await apiFetch('/hospitais');
    const grid = document.getElementById('all-hospitals');
    if (!grid) return;
    grid.innerHTML = list.map(item => `
      <a class="hospital-card page-enter" href="#/hospital/${encodeURIComponent(item.slug || item.hospital)}">
        <div class="hospital-icon">${ICONS.hospital}</div>
        <div>
          <div class="hospital-name">${escHtml(item.hospital)}</div>
          <div class="hospital-count">${item.count || 0} médico${item.count !== 1 ? 's' : ''}</div>
        </div>
      </a>
    `).join('');
  } catch (err) {
    const grid = document.getElementById('all-hospitals');
    if (grid) grid.innerHTML = `<div class="text-muted">Erro ao carregar hospitais.</div>`;
  }
}

// ─── CHAT PAGE ───────────────────────────────────────────
let chatHistory = [];
let chatIsSending = false;

function renderChatPage(app, prefilledMedico = '') {
  app.innerHTML = `
    <div class="chat-page">
      <div class="chat-page-header">
        ${breadcrumb([{label:'Início',href:'#/'},{label:'Assistente IA'}])}
        <div class="chat-page-title">
          ${ICONS.chat}
          Assistente IA
        </div>
        <div class="chat-page-subtitle">Pergunte sobre médicos, especialidades e avaliações em Porto Alegre.</div>
      </div>
      <div class="chat-messages-area" id="chat-messages-area">
        <div class="chat-message bot">
          <div class="chat-bot-avatar">${ICONS.heart}</div>
          <div class="chat-bubble-group">
            <div class="chat-bubble">
              Olá! Sou o assistente do MedicoAI. Posso ajudar a encontrar médicos em Porto Alegre, comparar avaliações e responder dúvidas sobre especialistas. O que você precisa?
            </div>
            <div class="chat-chips" id="chat-chips">
              <button class="chat-chip" data-text="Melhores cardiologistas em Porto Alegre">Melhores cardiologistas</button>
              <button class="chat-chip" data-text="Médicos que aceitam Unimed">Aceita Unimed</button>
              <button class="chat-chip" data-text="Dermatologista bem avaliado">Dermatologista</button>
              <button class="chat-chip" data-text="Pediatra próximo ao centro">Pediatra</button>
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input-area">
        <input type="text" id="chat-input" placeholder="Pergunte sobre médicos, avaliações, indicações..." autocomplete="off" />
        <button id="send-btn" aria-label="Enviar">
          ${ICONS.send}
        </button>
      </div>
    </div>
  `;

  chatHistory = [];
  chatIsSending = false;

  const messagesArea = document.getElementById('chat-messages-area');
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');

  if (prefilledMedico) {
    input.value = `Fale sobre o médico ${prefilledMedico}`;
  }

  function scrollChat() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function addChatMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `chat-message ${sender}`;
    if (sender === 'bot') {
      div.innerHTML = `
        <div class="chat-bot-avatar">${ICONS.heart}</div>
        <div class="chat-bubble-group"><div class="chat-bubble">${formatMarkdown(text)}</div></div>
      `;
    } else {
      div.innerHTML = `
        <div class="chat-bubble-group"><div class="chat-bubble">${escHtml(text)}</div></div>
      `;
    }
    messagesArea.appendChild(div);
    scrollChat();
    return div;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'chat-message bot';
    div.id = 'typing-indicator';
    div.innerHTML = `
      <div class="chat-bot-avatar">${ICONS.heart}</div>
      <div class="chat-bubble-group">
        <div class="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    messagesArea.appendChild(div);
    scrollChat();
    return div;
  }

  async function sendChatMessage() {
    if (chatIsSending) return;
    const text = (input.value || '').trim();
    if (!text) return;

    const chips = document.getElementById('chat-chips');
    if (chips) chips.remove();

    input.value = '';
    chatIsSending = true;
    input.disabled = true;
    sendBtn.disabled = true;

    addChatMessage(text, 'user');
    chatHistory.push({ role: 'user', content: text });

    const typing = showTyping();

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, conversation_history: chatHistory.slice(-10) }),
      });
      typing.remove();
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const reply = data.response || 'Sem resposta do servidor.';
      addChatMessage(reply, 'bot');
      chatHistory.push({ role: 'assistant', content: reply });
    } catch (err) {
      typing.remove();
      addChatMessage('Desculpe, ocorreu um erro ao contatar o servidor. Tente novamente.', 'bot');
      console.error('[MedicoAI] Chat error:', err);
    } finally {
      chatIsSending = false;
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener('click', sendChatMessage);
  input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); } });
  messagesArea.addEventListener('click', e => {
    const chip = e.target.closest('.chat-chip');
    if (chip) { input.value = chip.dataset.text; sendChatMessage(); }
  });

  if (prefilledMedico) {
    setTimeout(() => sendChatMessage(), 200);
  } else {
    input.focus();
  }
}

// =========================================================
//   ROUTER
// =========================================================

function getRoute() {
  const hash = window.location.hash.slice(1) || '/';
  return hash;
}

function navigate(path) {
  window.location.hash = path;
}

function parseHash(hash) {
  const [pathPart, queryPart] = hash.split('?');
  const segments = pathPart.replace(/^\//, '').split('/').filter(Boolean);
  const params = {};
  if (queryPart) {
    for (const [k, v] of new URLSearchParams(queryPart)) params[k] = v;
  }
  return { segments, params };
}

async function router() {
  const app = document.getElementById('app');
  if (!app) return;

  const hash = getRoute();
  const { segments, params } = parseHash(hash);

  // Update active nav links
  document.querySelectorAll('.nav-link, .nav-link-mobile').forEach(el => {
    el.classList.remove('active');
    const href = el.getAttribute('href');
    if (href && (href === `#${hash}` || (href === '#/' && hash === '/'))) {
      el.classList.add('active');
    }
  });

  // Close mobile menu
  const mobileMenu = document.getElementById('navbar-mobile-menu');
  if (mobileMenu) mobileMenu.classList.remove('open');

  // Route matching
  if (segments.length === 0 || hash === '/') {
    await renderHome(app);
  }
  else if (segments[0] === 'especialidade' && segments[1]) {
    const slug = decodeURIComponent(segments[1]);
    await renderList(app, {
      type: 'especialidade',
      slug,
      title: slug,
      apiPath: `/especialidades/${encodeURIComponent(slug)}`,
      breadcrumbs: breadcrumb([
        {label:'Início', href:'#/'},
        {label:'Especialidades', href:'#/especialidades'},
        {label: slug},
      ]),
    });
  }
  else if (segments[0] === 'hospital' && segments[1]) {
    const slug = decodeURIComponent(segments[1]);
    await renderList(app, {
      type: 'hospital',
      slug,
      title: slug,
      apiPath: `/hospitais/${encodeURIComponent(slug)}`,
      breadcrumbs: breadcrumb([
        {label:'Início', href:'#/'},
        {label:'Hospitais', href:'#/hospitais'},
        {label: slug},
      ]),
    });
  }
  else if (segments[0] === 'medico' && segments[1]) {
    await renderProfile(app, decodeURIComponent(segments[1]));
  }
  else if (segments[0] === 'busca') {
    const q = params.q || '';
    await renderList(app, {
      type: 'busca',
      query: q,
      title: `Busca: "${q}"`,
      apiPath: `/search?q=${encodeURIComponent(q)}`,
      breadcrumbs: breadcrumb([
        {label:'Início', href:'#/'},
        {label: `Busca: "${q}"`},
      ]),
    });
  }
  else if (segments[0] === 'especialidades') {
    await renderSpecialtiesPage(app);
  }
  else if (segments[0] === 'hospitais') {
    await renderHospitalsPage(app);
  }
  else if (segments[0] === 'chat') {
    const medicoName = params.medico || '';
    renderChatPage(app, medicoName);
  }
  else {
    // 404
    app.innerHTML = `
      <div class="list-page">
        <div class="empty-state" style="padding:100px 24px">
          <div class="empty-state-icon">${ICONS.search}</div>
          <div class="empty-state-title">Página não encontrada</div>
          <div class="empty-state-text">A página que você procura não existe.</div>
          <a href="#/" style="margin-top:24px;display:inline-block" class="btn-primary">Ir para o início</a>
        </div>
      </div>
    `;
  }

  // Scroll to top on navigation
  window.scrollTo(0, 0);
}

// =========================================================
//   NAVBAR INTERACTIONS
// =========================================================

function initNavbar() {
  const menuBtn = document.getElementById('navbar-menu-btn');
  const mobileMenu = document.getElementById('navbar-mobile-menu');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
    });
  }

  // Desktop search
  const navSearchInput = document.getElementById('navbar-search-input');
  if (navSearchInput) {
    navSearchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const q = navSearchInput.value.trim();
        if (q) { navigate(`/busca?q=${encodeURIComponent(q)}`); navSearchInput.value = ''; }
      }
    });
  }

  // Mobile search
  const mobileSearchInput = document.getElementById('navbar-mobile-search-input');
  if (mobileSearchInput) {
    mobileSearchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const q = mobileSearchInput.value.trim();
        if (q) { navigate(`/busca?q=${encodeURIComponent(q)}`); mobileSearchInput.value = ''; }
      }
    });
  }

  // Sticky shadow on scroll
  window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
      if (window.scrollY > 10) navbar.style.boxShadow = '0 2px 16px rgba(0,0,0,0.10)';
      else navbar.style.boxShadow = '';
    }
  }, { passive: true });

  // Footer height fix: ensure footer is always at bottom
  const footer = document.querySelector('.site-footer');
  if (footer) {
    // If page content is very short, footer still sticks to bottom (handled by flex on body)
  }
}

// =========================================================
//   INIT
// =========================================================

window.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  router();
});

window.addEventListener('hashchange', () => {
  router();
});
