requireAuth();

async function loadAlerts() {
  const res = await apiCall('/alerts');

  if (res.error) {
    alert(res.error);
    return;
  }

  const tbody = document.getElementById('alerts-table');
  tbody.innerHTML = '';

  // ✅ Safety check
  const items = res.items || [];

  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5">No alerts found</td></tr>`;
    return;
  }

  items.forEach(a => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${a.timestamp || '-'}</td>
      <td>${a.severity || '-'}</td>
      <td>${a.reason_code || '-'}</td>
      <td>${a.status || '-'}</td>
      <td>${a.notes || '-'}</td>
    `;

    tbody.appendChild(tr);
  });
}

// Initial load
loadAlerts();