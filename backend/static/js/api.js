async function apiCall(endpoint, options = {}) {
  try {
    const token = getToken();

    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    });

    clearTimeout(timeout);

    if (res.status === 401) {
      clearToken();
      window.location.href = '/';
      return { error: 'Unauthorized' };
    }

    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }

    if (!res.ok) {
      return { error: data.msg || data.message || `HTTP ${res.status}` };
    }

    return data;

  } catch (err) {
    return { error: 'Server not reachable. Please try again later.' };
  }
}