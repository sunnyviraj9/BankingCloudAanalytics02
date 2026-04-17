#!/bin/bash

# Banking Cloud Analytics - Deployment Script
# This script helps deploy the application on EC2

echo "=========================================="
echo "Banking Cloud Analytics - Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root"
    exit 1
fi

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "Installing Python and pip..."
sudo apt install python3 python3-pip -y

# Install application dependencies
echo "Installing application dependencies..."
cd backend
pip3 install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create backend/.env with the following:"
    echo ""
    echo "AWS_REGION=us-east-1"
    echo "AWS_ACCESS_KEY_ID=your_access_key"
    echo "AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "JWT_SECRET_KEY=your_jwt_secret"
    echo ""
    read -p "Press Enter to continue after creating .env file..."
fi

# Test application
echo ""
echo "Testing application..."
python3 -c "import app; print('✅ App imports successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Application setup successful!"
else
    echo "❌ Application setup failed!"
    exit 1
fi

# Ask if user wants to setup systemd service
echo ""
read -p "Do you want to setup systemd service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating systemd service..."
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    
    # Create service file
    sudo tee /etc/systemd/system/banking-app.service > /dev/null <<EOF
[Unit]
Description=Banking Cloud Analytics
After=network.target

[Service]
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$HOME/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    # Start service
    sudo systemctl start banking-app
    
    # Enable on boot
    sudo systemctl enable banking-app
    
    echo "✅ Systemd service created and started!"
    echo ""
    echo "Service commands:"
    echo "  Start:   sudo systemctl start banking-app"
    echo "  Stop:    sudo systemctl stop banking-app"
    echo "  Restart: sudo systemctl restart banking-app"
    echo "  Status:  sudo systemctl status banking-app"
    echo "  Logs:    sudo journalctl -u banking-app -f"
fi

# Ask if user wants to setup Nginx
echo ""
read -p "Do you want to setup Nginx? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Nginx..."
    sudo apt install nginx -y
    
    read -p "Enter your domain name (or EC2 public IP): " DOMAIN
    
    # Create Nginx config
    sudo tee /etc/nginx/sites-available/banking-app > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static {
        alias $CURRENT_DIR/static;
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/banking-app /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx config
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        # Restart Nginx
        sudo systemctl restart nginx
        echo "✅ Nginx configured and started!"
    else
        echo "❌ Nginx configuration error!"
    fi
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application should be running at:"
echo "  http://your-server-ip:5000"
echo ""
echo "If you configured Nginx:"
echo "  http://$DOMAIN"
echo ""
echo "Next steps:"
echo "1. Ensure your .env file is configured"
echo "2. Check application logs: sudo journalctl -u banking-app -f"
echo "3. Configure your security group to allow HTTP/HTTPS"
echo "4. (Optional) Setup SSL with: sudo certbot --nginx -d $DOMAIN"
echo ""
