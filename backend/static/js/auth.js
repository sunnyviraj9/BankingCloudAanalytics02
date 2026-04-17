// auth.js - Authentication Module

// =======================
// 🔐 LOGIN FUNCTION
// =======================
async function loginUser() {
  const email = document.getElementById('lemail').value.trim();
  const password = document.getElementById('lpass').value.trim();
  const msgBox = document.getElementById('login-msg');

  // Check DB connection first
  try {
    const healthRes = await fetch('/api/health');
    if (!healthRes.ok) {
      showMessage(msgBox, 'Database connection lost. Please try again later.', 'error');
      return;
    }
  } catch (err) {
    showMessage(msgBox, 'Cannot reach server. Check your connection.', 'error');
    return;
  }

  if (!email || !password) {
    showMessage(msgBox, 'Please fill all fields', 'error');
    return;
  }

  showMessage(msgBox, 'Logging in...', 'info');

  try {
    const res = await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    // ❌ ERROR CASE
    if (!res || !res.token) {
      showMessage(msgBox, res?.msg || 'Invalid email or password', 'error');
      return;
    }

    // ✅ SUCCESS
    setToken(res.token);
    showMessage(msgBox, 'Login successful! Redirecting...', 'success');

    // 🔥 REDIRECT TO FLASK ROUTE
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 500);

  } catch (err) {
    showMessage(msgBox, 'Server error. Try again.', 'error');
    console.error(err);
  }
}

// =======================
// 📝 REGISTER FUNCTION
// =======================
async function registerUser() {
  const email = document.getElementById('remail').value.trim();
  const password = document.getElementById('rpass').value.trim();
  const msgBox = document.getElementById('register-msg');

  // Check DB connection first
  try {
    const healthRes = await fetch('/api/health');
    if (!healthRes.ok) {
      showMessage(msgBox, 'Database connection lost. Please try again later.', 'error');
      return;
    }
  } catch (err) {
    showMessage(msgBox, 'Cannot reach server. Check your connection.', 'error');
    return;
  }

  if (!email || !password) {
    showMessage(msgBox, 'Please fill all fields', 'error');
    return;
  }

  if (password.length < 6) {
    showMessage(msgBox, 'Password must be at least 6 characters', 'error');
    return;
  }

  showMessage(msgBox, 'Registering...', 'info');

  try {
    const res = await apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    // ❌ ERROR CASE
    if (!res || res.msg !== "User registered successfully") {
      showMessage(msgBox, res?.msg || 'Registration failed', 'error');
      return;
    }

    // ✅ SUCCESS
    showMessage(msgBox, 'Registered successfully! Switching to login...', 'success');

    // 🔥 CLEAR INPUTS & SWITCH TO LOGIN TAB
    document.getElementById('remail').value = '';
    document.getElementById('rpass').value = '';
    
    setTimeout(() => {
      document.getElementById('login').classList.add('active');
      document.getElementById('register').classList.remove('active');
      document.querySelectorAll('.tab-button')[0].classList.add('active');
      document.querySelectorAll('.tab-button')[1].classList.remove('active');
    }, 1000);

  } catch (err) {
    showMessage(msgBox, 'Server error. Try again.', 'error');
    console.error(err);
  }
}

// =======================
// 🚪 LOGOUT FUNCTION
// =======================
function logout() {
  localStorage.removeItem('token');
  window.location.href = '/';
}

// =======================
// 🔍 CHECK AUTHENTICATION
// =======================
function checkAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = '/';
    return false;
  }
  return true;
}

// =======================
// 💬 MESSAGE HELPER
// =======================
function showMessage(msgBox, text, type) {
  msgBox.classList.remove('error', 'success', 'info');
  msgBox.classList.add('show', type);
  msgBox.innerText = text;
}

