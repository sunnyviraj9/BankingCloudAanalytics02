# Banking Cloud Analytics

## Setup

1. Install dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

2. Copy env:
   ```
   cp .env.example .env
   ```
   Edit `.env` with your AWS DynamoDB credentials.

3. Run:
   ```
   python app.py
   ```

4. Open http://localhost:5000

## DB Fixes Applied
- Auto-creates DynamoDB tables with GSIs
- bcrypt passwords
- User-scoped accounts/transactions
- Efficient GSI queries (no scans)
- Atomic tx + balance updates
- Auth protected endpoints

## AWS Setup
- Create DynamoDB tables manually or let app create
- IAM role with DynamoDB full access (dev)

