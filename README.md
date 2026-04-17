# Banking Cloud Analytics

A simple banking application with transaction tracking, account management, and financial analytics.

## Features

- User Authentication (JWT)
- Account Management (DynamoDB)
- Transaction History (CSV-based)
- Financial Analytics Dashboard
- Responsive UI (Bootstrap 5)

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: AWS DynamoDB
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: JWT with bcrypt

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env` file:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

### 3. Run Application

```bash
cd backend
python app.py
```

Visit: http://127.0.0.1:5000

## Project Structure

```
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables (not in git)
│   ├── static/            # CSS and JavaScript
│   └── templates/         # HTML templates
├── december_2025.csv      # Transaction data
├── transactions_jan_2026.csv
├── transactions_feb_2026.csv
└── .gitignore
```

## Pages

1. **Dashboard** - Account overview and recent transactions
2. **Accounts** - Create and manage bank accounts
3. **Transactions** - View and filter transaction history
4. **Analytics** - Financial insights with charts

## Deployment

See `DEPLOYMENT.md` for EC2 deployment instructions.

## License

MIT
