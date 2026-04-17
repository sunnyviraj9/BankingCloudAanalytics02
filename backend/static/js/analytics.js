requireAuth();

let chart = null;
let currentAccountId = null;

async function loadAccounts() {
  const res = await apiCall('/accounts');
  if (res.error) return alert(res.error);

  const select = document.getElementById('account-select');
  select.innerHTML = ''; // ✅ clear old

  res.accounts.forEach(acc => {
    const opt = document.createElement('option');
    opt.value = acc.id;                          // ✅ FIXED
    opt.text = `${acc.type} (${acc.id})`;        // ✅ FIXED
    select.appendChild(opt);
  });

  if (res.accounts.length) {
    currentAccountId = res.accounts[0].id;       // ✅ FIXED
    select.value = currentAccountId;
  }

  select.onchange = () => {
    currentAccountId = select.value;
    loadAnalytics();
  };

  await loadAnalytics();
}

async function loadAnalytics() {
  if (!currentAccountId) return;

  const from = document.getElementById('from').value;
  const to = document.getElementById('to').value;

  const params = new URLSearchParams({
    account_id: currentAccountId,
    ...(from ? { from } : {}),
    ...(to ? { to } : {})
  });

  const res = await apiCall(`/analytics/summary?${params.toString()}`);
  if (res.error) return alert(res.error);

  // ✅ FIXED (no cents conversion)
  document.getElementById('inflow').innerText = `$${res.total_inflow}`;
  document.getElementById('outflow').innerText = `$${res.total_outflow}`;
  document.getElementById('count').innerText = res.tx_count;

  const ctx = document.getElementById('chart').getContext('2d');

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: res.chart?.labels || [],
      datasets: [
        {
          label: 'Balance',
          data: res.chart?.balance_points || [],
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37,99,235,0.2)',
          fill: true
        }
      ]
    },
    options: {
      responsive: true
    }
  });
}

// Load button
document.getElementById('btn-load').onclick = loadAnalytics;

// Initial load
loadAccounts();