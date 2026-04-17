from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import uuid
import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal
from dotenv import load_dotenv
import bcrypt
import time

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-me')

jwt = JWTManager(app)
CORS(app)

# ============================
# 🔗 DynamoDB Connection with Auto-Create & Health Check
# ============================
region = os.getenv('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)

# Global table references (persistent)
users_table = None
accounts_table = None
transactions_table = None
db_connection_error = None

def init_tables():
    """Initialize table references with error handling"""
    global users_table, accounts_table, transactions_table, db_connection_error
    try:
        users_table = dynamodb.Table('users')
        accounts_table = dynamodb.Table('accounts')
        transactions_table = dynamodb.Table('transactions')
        
        # Test connection
        users_table.table_status
        db_connection_error = None
        print("✅ DynamoDB tables initialized successfully")
        return True
    except Exception as e:
        db_connection_error = str(e)
        print(f"❌ DynamoDB connection error: {e}")
        return False

def check_db_connection():
    """Verify DynamoDB connection is active"""
    global db_connection_error
    try:
        if users_table and accounts_table and transactions_table:
            # Quick connection test
            dynamodb.meta.client.describe_table(TableName='users')
            db_connection_error = None
            return True
        return False
    except Exception as e:
        db_connection_error = str(e)
        return False

def create_tables_if_not_exist():
    tables = [
        {
            'TableName': 'users',
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'GlobalSecondaryIndexes': [{'IndexName': 'email-index', 'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}], 'Projection': {'ProjectionType': 'ALL'}}]
        },
        {
            'TableName': 'accounts',
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'GlobalSecondaryIndexes': [{'IndexName': 'user-index', 'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}], 'Projection': {'ProjectionType': 'ALL'}}]
        },
        {
            'TableName': 'transactions',
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'account_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'N'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'GlobalSecondaryIndexes': [{'IndexName': 'account-timestamp-index', 'KeySchema': [{'AttributeName': 'account_id', 'KeyType': 'HASH'}, {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}], 'Projection': {'ProjectionType': 'ALL'}}]
        }
    ]
    
    client = dynamodb.meta.client
    
    for table_config in tables:
        try:
            client.describe_table(TableName=table_config['TableName'])
            print(f"✅ Table {table_config['TableName']} exists")
        except client.exceptions.ResourceNotFoundException:
            print(f"🔄 Creating table {table_config['TableName']}...")
            client.create_table(**table_config)
            client.get_waiter('table_exists').wait(TableName=table_config['TableName'])
            print(f"✅ Table {table_config['TableName']} created successfully")
        except Exception as e:
            print(f"❌ Error with {table_config['TableName']}: {e}")

# Initialize tables and connection
create_tables_if_not_exist()
init_tables()


# =========================================================
# 🔐 AUTH ROUTES
# =========================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check DynamoDB connection status"""
    if check_db_connection():
        return jsonify({"status": "connected", "message": "DynamoDB connection OK"}), 200
    else:
        return jsonify({"status": "disconnected", "message": db_connection_error}), 503

@app.route('/auth/register', methods=['POST'])
def register():
    if not check_db_connection():
        return jsonify({"msg": "Database connection lost. Please try again."}), 503
    
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

# Check existing user (fallback scan since GSI issue)
    try:
        response = users_table.query(
            IndexName='email-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )
        if response.get('Items'):
            return jsonify({"msg": "User already exists"}), 400
    except:
        # Fallback to scan if GSI not ready
        response = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email))
        if response.get('Items'):
            return jsonify({"msg": "User already exists"}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create user
    new_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": hashed
    }

    users_table.put_item(Item=new_user)

    return jsonify({"msg": "User registered successfully"}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    if not check_db_connection():
        return jsonify({"msg": "Database connection lost. Please try again."}), 503
    
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

# Query by email (fallback scan)
    try:
        response = users_table.query(
            IndexName='email-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )
        user = response.get('Items', [None])[0]
    except:
        # Fallback scan
        response = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email))
        user = response.get('Items', [None])[0]

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = create_access_token(identity=user['id'])

        return jsonify({
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email']
            }
        })

    return jsonify({"msg": "Invalid credentials"}), 401


# =========================================================
# 🏦 ACCOUNTS API
# =========================================================

@app.route('/api/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    current_user_id = get_jwt_identity()
    try:
        # Try using the GSI first
        response = accounts_table.query(
            IndexName='user-index',
            KeyConditionExpression=Key('user_id').eq(current_user_id)
        )
        return jsonify({"accounts": response.get('Items', [])})
    except Exception as e:
        # Fallback to scan if GSI not ready
        print(f"GSI not ready, using scan: {e}")
        response = accounts_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(current_user_id)
        )
        return jsonify({"accounts": response.get('Items', [])})


@app.route('/api/accounts', methods=['POST'])
@jwt_required()
def create_account():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name")
    acc_type = data.get("type")

    if not name or not acc_type:
        return jsonify({"msg": "Missing name or type"}), 400

    new_account = {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": acc_type,
        "status": "active",
        "balance": Decimal('0.0'),
        "user_id": current_user_id
    }

    accounts_table.put_item(Item=new_account)

    return jsonify({"msg": "Account created successfully"}), 201


# =========================================================
# 💸 TRANSACTIONS API
# =========================================================

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    response = transactions_table.scan()
    return jsonify({"transactions": response.get('Items', [])})


@app.route('/api/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    amount = Decimal(str(data.get("amount")))
    tx_type = data.get("type")
    account_id = data.get("account_id")
    desc = data.get("desc", "")

    if not amount or not tx_type or not account_id:
        return jsonify({"msg": "Missing required fields"}), 400

    # Verify account belongs to user
    account_response = accounts_table.get_item(Key={'id': account_id})
    account = account_response.get('Item')
    if not account or account['user_id'] != current_user_id:
        return jsonify({"msg": "Account not found or unauthorized"}), 403

    timestamp = int(time.time() * 1000)
    delta = amount if tx_type == 'credit' else -amount

    new_tx = {
        "id": str(uuid.uuid4()),
        "amount": str(amount),
        "type": tx_type,
        "account_id": account_id,
        "desc": desc,
        "timestamp": timestamp,
        "user_id": current_user_id
    }

    # Atomic update: add tx & update balance
    dynamodb.meta.client.transact_write_items(
        TransactItems=[
            {
                'Put': {
                    'TableName': 'transactions',
                    'Item': new_tx
                }
            },
            {
                'Update': {
                    'TableName': 'accounts',
                    'Key': {'id': account_id},
                    'UpdateExpression': 'ADD balance :delta',
                    'ExpressionAttributeValues': {':delta': delta}
                }
            }
        ]
    )

    return jsonify({"msg": "Transaction added and balance updated"}), 201


# =========================================================
# 🌐 FRONTEND ROUTES (IMPORTANT FIX)
# =========================================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/accounts-page')
def accounts_page():
    return render_template('accounts.html')


@app.route('/transactions-page')
def transactions_page():
    return render_template('transactions.html')


@app.route('/analytics-page')
def analytics_page():
    return render_template('analytics.html')


# =========================================================
# 📊 CSV TRANSACTIONS API
# =========================================================

@app.route('/api/csv-transactions', methods=['GET'])
def get_csv_transactions():
    """Load transactions from CSV files"""
    import csv
    
    all_transactions = []
    csv_files = ['december_2025.csv', 'transactions_jan_2026.csv', 'transactions_feb_2026.csv']
    
    for csv_file in csv_files:
        # CSV files are in the root directory (parent of backend)
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), csv_file)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Skip opening/closing balance entries
                        if row.get('category') not in ['opening_balance', 'closing_balance']:
                            all_transactions.append({
                                'date': row.get('date', ''),
                                'description': row.get('description', ''),
                                'amount': row.get('amount', '0'),
                                'type': row.get('type', ''),
                                'category': row.get('category', '')
                            })
                print(f"✅ Loaded {csv_file}: {len([t for t in all_transactions])} transactions")
            except Exception as e:
                print(f"❌ Error reading {csv_file}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"📊 Total transactions loaded: {len(all_transactions)}")
    return jsonify({"transactions": all_transactions})


@app.route('/api/csv-summary', methods=['GET'])
def get_csv_summary():
    """Get summary of CSV transactions (total credits, debits, net balance)"""
    import csv
    
    total_credits = 0
    total_debits = 0
    csv_files = ['december_2025.csv', 'transactions_jan_2026.csv', 'transactions_feb_2026.csv']
    
    for csv_file in csv_files:
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), csv_file)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        category = row.get('category', '')
                        if category not in ['opening_balance', 'closing_balance']:
                            amount = float(row.get('amount', 0))
                            tx_type = row.get('type', '')
                            
                            if tx_type == 'credit':
                                total_credits += amount
                            elif tx_type == 'debit':
                                total_debits += amount
            except Exception as e:
                print(f"❌ Error reading {csv_file}: {e}")
    
    net_balance = total_credits - total_debits
    
    return jsonify({
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_balance": net_balance
    })


# =========================================================
# ▶️ RUN APP
# =========================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)