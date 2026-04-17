import pytest
from app import app  # Import the Flask app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Black Box Testing: Test API endpoints without knowing internal implementation

def test_register_success(client):
    """Test user registration with valid data"""
    data = {'email': 'test@example.com', 'password': 'password123'}
    response = client.post('/auth/register', json=data)
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_register_missing_fields(client):
    """Test registration with missing fields"""
    data = {'email': 'test@example.com'}
    response = client.post('/auth/register', json=data)
    assert response.status_code == 400
    assert b'Missing email or password' in response.data

def test_register_duplicate_user(client):
    """Test registering a user that already exists"""
    data = {'email': 'test@example.com', 'password': 'password123'}
    client.post('/auth/register', json=data)  # First registration
    response = client.post('/auth/register', json=data)  # Duplicate
    assert response.status_code == 400
    assert b'User already exists' in response.data

def test_login_success(client):
    """Test login with correct credentials"""
    # First register
    data = {'email': 'test@example.com', 'password': 'password123'}
    client.post('/auth/register', json=data)
    # Then login
    response = client.post('/auth/login', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data

def test_login_invalid_credentials(client):
    """Test login with wrong password"""
    data = {'email': 'test@example.com', 'password': 'wrongpassword'}
    response = client.post('/auth/login', json=data)
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_get_accounts_empty(client):
    """Test getting accounts when none exist"""
    response = client.get('/accounts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['accounts'] == []

def test_create_account_success(client):
    """Test creating an account with valid data"""
    data = {'name': 'Savings Account', 'type': 'savings'}
    response = client.post('/accounts', json=data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['name'] == 'Savings Account'
    assert data['type'] == 'savings'
    assert data['balance'] == 0.0

def test_create_account_missing_fields(client):
    """Test creating account with missing fields"""
    data = {'name': 'Savings Account'}
    response = client.post('/accounts', json=data)
    assert response.status_code == 400
    assert b'Missing name or type' in response.data

def test_get_transactions_empty(client):
    """Test getting transactions when none exist"""
    response = client.get('/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['transactions'] == []

def test_add_transaction_deposit(client):
    """Test adding a deposit transaction"""
    # First create an account
    acc_data = {'name': 'Savings Account', 'type': 'savings'}
    acc_response = client.post('/accounts', json=acc_data)
    acc_id = json.loads(acc_response.data)['id']

    # Then add transaction
    tx_data = {'amount': 100.0, 'type': 'deposit', 'account_id': acc_id, 'desc': 'Initial deposit'}
    response = client.post('/transactions', json=tx_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['amount'] == 100.0
    assert data['type'] == 'deposit'

def test_add_transaction_withdraw_insufficient_balance(client):
    """Test withdrawing more than balance"""
    # Create account and deposit
    acc_data = {'name': 'Savings Account', 'type': 'savings'}
    acc_response = client.post('/accounts', json=acc_data)
    acc_id = json.loads(acc_response.data)['id']
    client.post('/transactions', json={'amount': 50.0, 'type': 'deposit', 'account_id': acc_id})

    # Try to withdraw more
    tx_data = {'amount': 100.0, 'type': 'withdraw', 'account_id': acc_id}
    response = client.post('/transactions', json=tx_data)
    assert response.status_code == 400
    assert b'Insufficient balance' in response.data

def test_add_transaction_invalid_account(client):
    """Test adding transaction to non-existent account"""
    tx_data = {'amount': 100.0, 'type': 'deposit', 'account_id': 'invalid-id'}
    response = client.post('/transactions', json=tx_data)
    assert response.status_code == 404
    assert b'Account not found' in response.data

def test_get_analytics(client):
    """Test getting analytics data"""
    response = client.get('/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'inflow' in data
    assert 'outflow' in data
    assert 'net' in data
    assert 'transaction_count' in data

def test_get_alerts(client):
    """Test getting alerts"""
    response = client.get('/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'alerts' in data

def test_get_admin_logs(client):
    """Test getting admin logs"""
    response = client.get('/admin/logs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'logs' in data
    assert len(data['logs']) > 0