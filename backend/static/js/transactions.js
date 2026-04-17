requireAuth();

let page = 1;
let currentAccountId = null;

async function loadAccounts() {
  const res = await apiCall('/accounts');
  if (res.error) return alert(res.error);

  const select = document.getElementById('account-select');
  select.innerHTML = ''; // ✅ clear old options

  res.accounts.forEach(acc => {
    const opt = document.createElement('option');
    opt.value = acc.id;                          // ✅ fixed
    opt.text = `${acc.type} (${acc.id})`;        // ✅ fixed
    select.appendChild(opt);
  });

  if (res.accounts.length) {
    currentAccountId = res.accounts[0].id;       // ✅ fixed
    select.value = currentAccountId;
  }

  select.onchange = () => {
    currentAccountId = select.value;
    loadTxns();
  };

  await loadTxns();
}

async function loadTxns() {
  if (!currentAccountId) return;

  const from = document.getElementById('from').value;
  const to = document.getElementById('to').value;
  const type = document.getElementById('type').value;

  const params = new URLSearchParams({
    account_id: currentAccountId,
    page,
    limit: 10,
    ...(from ? { from } : {}),
    ...(to ? { to } : {}),
    ...(type ? { type } : {})
  });

  const res = await apiCall(`/tx/history?${params.toString()}`);
  if (res.error) return alert(res.error);

  const tbody = document.getElementById('tx-table');
  tbody.innerHTML = '';

  res.items.forEach(tx => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${tx.timestamp}</td>
      <td>${tx.type}</td>
      <td>${tx.amount}</td>          <!-- ✅ fixed -->
      <td>${tx.description || '-'}</td>
    `;

    tbody.appendChild(tr);
  });

  document.getElementById('page').innerText = page;
}

// Pagination
document.getElementById('btn-load').onclick = () => {
  page = 1;
  loadTxns();
};

document.getElementById('btn-prev').onclick = () => {
  if (page > 1) page--;
  loadTxns();
};

document.getElementById('btn-next').onclick = () => {
  page++;
  loadTxns();
};

// Export
document.getElementById('btn-export').onclick = () => {
  const from = document.getElementById('from').value;
  const to = document.getElementById('to').value;
  const type = document.getElementById('type').value;

  const params = new URLSearchParams({
    account_id: currentAccountId,
    ...(from ? { from } : {}),
    ...(to ? { to } : {}),
    ...(type ? { type } : {}),
    export: 'csv'
  });

  window.open(`${API_BASE}/tx/history?${params.toString()}`, '_blank');
};

// Initial load
loadAccounts();