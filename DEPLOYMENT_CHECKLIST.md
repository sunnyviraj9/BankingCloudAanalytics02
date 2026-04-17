# Deployment Checklist

## ✅ Files Ready for GitHub

### Application Files
- ✅ `backend/app.py` - Main Flask application
- ✅ `backend/requirements.txt` - Python dependencies (includes gunicorn)
- ✅ `backend/static/` - CSS and JavaScript files
- ✅ `backend/templates/` - HTML templates
- ✅ `*.csv` - Transaction data files

### Configuration Files
- ✅ `.gitignore` - Excludes .env and sensitive files
- ✅ `backend/.env.example` - Example environment variables
- ✅ `README.md` - Project documentation
- ✅ `DEPLOYMENT.md` - Detailed deployment guide
- ✅ `deploy.sh` - Automated deployment script

### What's Excluded (via .gitignore)
- ❌ `.env` files (contains secrets)
- ❌ `__pycache__/` (Python cache)
- ❌ `.vscode/` (IDE settings)
- ❌ `*.log` (log files)
- ❌ Virtual environments

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables
- [ ] Create `backend/.env` file
- [ ] Add AWS credentials
- [ ] Add JWT secret key
- [ ] Verify AWS region

### 2. AWS Setup
- [ ] Create/verify DynamoDB tables
- [ ] Configure IAM permissions
- [ ] Setup security groups (ports 22, 80, 443)
- [ ] Launch EC2 instance

### 3. GitHub Repository
- [ ] Create GitHub repository
- [ ] Add remote: `git remote add origin <url>`
- [ ] Push code: `git push -u origin main`

### 4. EC2 Instance
- [ ] Connect via SSH
- [ ] Clone repository
- [ ] Run deployment script
- [ ] Configure .env file
- [ ] Test application

---

## 🚀 Quick Deployment Steps

### 1. Push to GitHub
```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Banking Cloud Analytics"

# Add remote
git remote add origin https://github.com/your-username/your-repo.git

# Push
git push -u origin main
```

### 2. Deploy to EC2
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Run deployment script
chmod +x deploy.sh
./deploy.sh

# Or manual deployment (see DEPLOYMENT.md)
```

### 3. Configure Environment
```bash
cd backend
nano .env
```

Add:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
JWT_SECRET_KEY=your_jwt_secret
```

### 4. Start Application
```bash
# Using systemd (recommended)
sudo systemctl start banking-app
sudo systemctl status banking-app

# Or manually
python3 app.py
```

---

## 🔒 Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] Strong JWT secret key generated
- [ ] AWS credentials secured (use IAM roles if possible)
- [ ] Security groups configured properly
- [ ] HTTPS enabled (use Certbot)
- [ ] Regular security updates scheduled

---

## 📊 Application Structure

```
your-repo/
├── backend/
│   ├── app.py                 # Main application
│   ├── requirements.txt       # Dependencies
│   ├── .env                   # Environment (NOT in git)
│   ├── .env.example          # Example env file
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── index.html
│       ├── dashboard.html
│       ├── accounts.html
│       ├── transactions.html
│       └── analytics.html
├── december_2025.csv
├── transactions_jan_2026.csv
├── transactions_feb_2026.csv
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── DEPLOYMENT_CHECKLIST.md
└── deploy.sh
```

---

## 🌐 Access URLs

After deployment:

- **Development**: http://localhost:5000
- **EC2 (direct)**: http://your-ec2-ip:5000
- **EC2 (with Nginx)**: http://your-ec2-ip
- **Production (with domain)**: https://your-domain.com

---

## 📝 Important Notes

### Environment Variables
Never commit `.env` files to GitHub. Always use `.env.example` as a template.

### AWS Credentials
Best practice: Use IAM roles attached to EC2 instead of access keys.

### DynamoDB Tables
Tables are created automatically on first run. Ensure proper permissions.

### CSV Files
Transaction CSV files are included in the repository. For production, consider:
- Moving to S3
- Using DynamoDB for transactions
- Implementing file upload feature

### Port Configuration
- Development: 5000
- Production with Nginx: 80/443
- Ensure security groups allow these ports

---

## 🔧 Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u banking-app -f

# Check Python errors
python3 backend/app.py
```

### Can't connect to DynamoDB
```bash
# Test AWS credentials
aws dynamodb list-tables --region us-east-1

# Check IAM permissions
```

### Port already in use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

---

## ✅ Final Checklist

Before going live:

- [ ] All tests passing
- [ ] .env configured correctly
- [ ] DynamoDB tables created
- [ ] Application starts without errors
- [ ] Can login and create accounts
- [ ] Transactions display correctly
- [ ] Analytics charts working
- [ ] HTTPS enabled (production)
- [ ] Monitoring setup
- [ ] Backup configured

---

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify AWS credentials
3. Review security group settings
4. Consult DEPLOYMENT.md

---

**Ready to deploy! 🚀**
