// config.js

const API_BASE = "http://127.0.0.1:5000";

const getToken = () => localStorage.getItem('token');
const setToken = (t) => localStorage.setItem('token', t);
const clearToken = () => localStorage.removeItem('token');
const isLoggedIn = () => !!getToken();

function logout() {
  clearToken();
  window.location.href = '/';
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/';
  }
}