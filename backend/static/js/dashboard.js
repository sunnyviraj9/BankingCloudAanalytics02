// Dashboard JavaScript - Simplified CRUD Operations

async function loadDashboard() {
  try {
    await loadAccounts();
    await loadTransactions();
  } catch (err) {
    console.error('❌ Error loading dashboard:', err);
  }
}

async function loadAccounts() {
  const res = await apiCall('/api/accounts');
  if (res.error) {
    console.error('❌ Error loading accounts:', res.error);
    return;
  }

  const accounts = res.accounts || [];
  document.getElementById('total-accounts').textContent = accounts.length;

  let totalBalance = 0;
  let tbody = document.getElementById('accounts-table');
  tbody.innerHTML = '';

  if (accounts.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No accounts yet. Click "New Account" to create one!</td></tr>';
    document.getElementById('total-balance').textContent = '$0.00';
    return;
  }

  accounts.forEach(acc => {
    const balance = parseFloat(acc.balance || 0) || 0;
    totalBalance += balance;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${acc.name || 'Unknown'}</td>
      <td><span class="badge bg-light text-dark">${acc.type || 'N/A'}</span></td>
      <td>$${balance.toFixed(2)}</td>
      <td><span class="badge bg-success">${acc.status || 'active'}</span></td>
    `;
    tbody.appendChild(row);
  });

  document.getElementById('total-balance').textContent = `$${totalBalance.toFixed(2)}`;
}

async function loadTransactions() {
  const res = await apiCall('/api/transactions');
  if (res.error) {
    console.error('❌ Error loading transactions:', res.error);
    return;
  }

  const transactions = res.transactions || [];
  document.getElementById('recent-tx-count').textContent = transactions.length;

  let tbody = document.getElementById('transactions-table');
  tbody.innerHTML = '';

  if (transactions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">No transactions yet</td></tr>';
    return;
  }

  // Show last 5 transactions
  transactions.slice(0, 5).forEach(tx => {
    const date = new Date(tx.timestamp || 0).toLocaleDateString();
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${date}</td>
      <td>Account</td>
      <td><span class="badge bg-${tx.type === 'credit' ? 'success' : 'danger'}">${tx.type}</span></td>
      <td>$${parseFloat(tx.amount || 0).toFixed(2)}</td>
      <td>${tx.desc || '-'}</td>
    `;
    tbody.appendChild(row);
  });
}

async function createAccount() {
  const name = document.getElementById('account-name').value.trim();
  const type = document.getElementById('account-type').value;
  const msgDiv = document.getElementById('account-msg');

  if (!name) {
    msgDiv.classList.remove('d-none');
    msgDiv.className = 'alert alert-danger d-block';
    msgDiv.textContent = '❌ Please enter account name';
    return;
  }

  msgDiv.classList.add('d-none');

  const res = await apiCall('/api/accounts', {
    method: 'POST',
    body: JSON.stringify({ name, type })
  });

  if (res.error) {
    msgDiv.classList.remove('d-none');
    msgDiv.className = 'alert alert-danger d-block';
    msgDiv.textContent = '❌ ' + res.error;
    return;
  }

  msgDiv.classList.remove('d-none');
  msgDiv.className = 'alert alert-success d-block';
  msgDiv.textContent = '✅ Account created successfully!';

  setTimeout(() => {
    document.getElementById('account-name').value = '';
    bootstrap.Modal.getInstance(document.getElementById('addAccountModal')).hide();
    loadDashboard();
  }, 1000);
}