requireAuth();

async function loadAudit() {
  const res = await apiCall('/admin/audit?limit=20');

  if (res.error) {
    alert(res.error);
    return;
  }

  const tbody = document.getElementById('audit-table');
  tbody.innerHTML = '';

  // ✅ Safety check
  const items = res.items || [];

  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5">No audit logs found</td></tr>`;
    return;
  }

  items.forEach(log => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${log.timestamp || '-'}</td>
      <td>${log.actor_user_id || '-'}</td>
      <td>${log.action || '-'}</td>
      <td>${log.resource || '-'}</td>
      <td>${log.ip || '-'}</td>
    `;

    tbody.appendChild(tr);
  });
}

// Initial load
loadAudit();