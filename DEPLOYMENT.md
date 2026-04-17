# AWS EC2 Deployment Guide

## Prerequisites

- AWS Account
- EC2 instance (Ubuntu 20.04 or later recommended)
- Security Group with ports 22 (SSH) and 80/443 (HTTP/HTTPS) open
- AWS DynamoDB access configured

## Step 1: Launch EC2 Instance

1. Go to AWS EC2 Console
2. Launch Instance:
   - **AMI**: Ubuntu Server 20.04 LTS
   - **Instance Type**: t2.micro (free tier) or t2.small
   - **Security Group**: Allow SSH (22), HTTP (80), HTTPS (443)
3. Create/Download key pair (.pem file)
4. Launch instance

## Step 2: Connect to EC2

```bash
# Change key permissions
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 3: Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Git
sudo apt install git -y

# Install Nginx (optional, for production)
sudo apt install nginx -y
```

## Step 4: Clone Repository

```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

## Step 5: Setup Application

```bash
# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Create .env file
nano .env
```

Add the following to `.env`:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

Save and exit (Ctrl+X, Y, Enter)

## Step 6: Configure AWS Credentials

### Option A: Using IAM Role (Recommended)

1. Create IAM Role with DynamoDB permissions
2. Attach role to EC2 instance
3. No need for AWS credentials in .env

### Option B: Using Access Keys

Already configured in .env file above

## Step 7: Test Application

```bash
# Run the application
python3 app.py
```

Visit: http://your-ec2-public-ip:5000

## Step 8: Production Setup with Gunicorn

```bash
# Install Gunicorn
pip3 install gunicorn

# Test Gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Step 9: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/banking-app.service
```

Add the following:
```ini
[Unit]
Description=Banking Cloud Analytics
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo/backend
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Save and exit.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start banking-app

# Enable on boot
sudo systemctl enable banking-app

# Check status
sudo systemctl status banking-app
```

## Step 10: Configure Nginx (Optional)

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/banking-app
```

Add the following:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/ubuntu/your-repo/backend/static;
    }
}
```

Save and exit.

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/banking-app /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 11: Setup SSL (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Step 12: Configure DynamoDB Tables

Tables will be created automatically on first run. Ensure your AWS credentials have DynamoDB permissions:

- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:UpdateItem`

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u banking-app -f

# Check if port is in use
sudo netstat -tulpn | grep 5000
```

### DynamoDB connection issues
```bash
# Test AWS credentials
aws dynamodb list-tables --region us-east-1

# Check IAM permissions
```

### Nginx issues
```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t
```

## Security Checklist

- [ ] Change default JWT_SECRET_KEY
- [ ] Use IAM roles instead of access keys
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure security groups properly
- [ ] Keep system updated
- [ ] Use strong passwords
- [ ] Enable CloudWatch monitoring
- [ ] Setup backup for DynamoDB

## Updating Application

```bash
# Pull latest changes
cd /home/ubuntu/your-repo
git pull

# Restart service
sudo systemctl restart banking-app
```

## Monitoring

```bash
# View application logs
sudo journalctl -u banking-app -f

# Check service status
sudo systemctl status banking-app

# Monitor system resources
htop
```

## Backup

### DynamoDB Backup
- Enable Point-in-Time Recovery in DynamoDB console
- Or use AWS Backup service

### CSV Files Backup
```bash
# Create backup script
nano backup.sh
```

Add:
```bash
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz *.csv
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

## Cost Optimization

- Use t2.micro for low traffic (free tier eligible)
- Use DynamoDB on-demand pricing for variable workload
- Enable CloudWatch alarms for cost monitoring
- Stop instance when not in use (development)

## Support

For issues, check:
1. Application logs: `sudo journalctl -u banking-app -f`
2. Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. System logs: `sudo tail -f /var/log/syslog`
