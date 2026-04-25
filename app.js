const API = 'http://localhost:8000';
// Semua halaman HTML sekarang diakses via http://localhost:8000/index.html dst.

// --- TOKEN ---
const Auth = {
  getToken: () => localStorage.getItem('st_token'),
  getUser: () => JSON.parse(localStorage.getItem('st_user') || 'null'),
  isLoggedIn: () => !!localStorage.getItem('st_token'),
  save: (token, user) => {
    localStorage.setItem('st_token', token);
    localStorage.setItem('st_user', JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem('st_token');
    localStorage.removeItem('st_user');
  }
};

// --- API HELPER ---
let _redirecting = false; // flag anti-loop untuk 401
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });

  // Kalau 401, token expired/rusak — bersihkan dan paksa login ulang
  // Tapi hanya sekali, cegah redirect loop
  if (res.status === 401) {
    if (!_redirecting) {
      _redirecting = true;
      Auth.clear();
      window.location.href = 'index.html';
    }
    return;
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Terjadi kesalahan');
  return data;
}

// --- TOAST ---
function showToast(msg, type = '') {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = type ? `show ${type}` : 'show';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 3000);
}

// --- NAV RENDER ---
function renderNav(activePage = '') {
  const user = Auth.getUser();
  const pages = [
    { href: 'leaderboard.html', label: 'Leaderboard' },
    { href: 'forum.html', label: 'Forum' },
    { href: 'cari.html', label: 'Cari Trader' },
  ];
  const navLinks = pages.map(p =>
    `<a href="${p.href}" class="${activePage === p.href ? 'active' : ''}">${p.label}</a>`
  ).join('');
  const navAuth = user
    ? `<a href="dashboard.html" class="btn btn-ghost btn-sm">${user.username}</a>
       <button class="btn btn-danger btn-sm" onclick="logout()">Keluar</button>`
    : `<a href="index.html" class="btn btn-ghost btn-sm">Masuk</a>
       <a href="index.html" class="btn btn-primary btn-sm">Daftar</a>`;
  document.querySelector('nav .nav-links').innerHTML = navLinks;
  document.querySelector('nav .nav-auth').innerHTML = navAuth;
}

function logout() {
  Auth.clear();
  window.location.href = 'index.html';
}

// --- AVATAR LETTER ---
function avatarLetter(name) {
  return (name || '?').charAt(0).toUpperCase();
}