requireAuth();

async function loadAccounts() {
  const res = await apiCall('/accounts');
  if (res.error) return alert(res.error);

  const tbody = document.getElementById('accounts-table');
  tbody.innerHTML = '';

  res.accounts.forEach(acc => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${acc.id}</td>
      <td>${acc.type}</td>
      <td>${acc.status}</td>
      <td>${acc.balance}</td>
    `;

    tbody.appendChild(tr);
  });
}

document.getElementById('btn-create').onclick = async () => {
  const type = document.getElementById('new-type').value;

  const res = await apiCall('/accounts', {
    method: 'POST',
    body: JSON.stringify({ type })   // ✅ fixed key
  });

  if (res.error) {
    document.getElementById('create-msg').innerText = res.error;
    return;
  }

  document.getElementById('create-msg').innerText = '';
  await loadAccounts();
};

// Initial load
loadAccounts();