#!/bin/bash

# ChatApp Deployment Script
# Automates deployment to production server

set -e

# Configuration
PROD_SERVER="prod-server-01.chatapp.com"
PROD_USER="chatapp"
PROD_PASSWORD="ChatApp_Prod_Deploy_2024!"
DB_PASSWORD="Ch@tApp_DB_P@ssw0rd!"
APP_DIR="/var/www/chatapp"

echo "==================================="
echo "ChatApp Production Deployment"
echo "==================================="
echo ""

# Check if we're on the main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $BRANCH"

# Build and deploy
echo "Building application..."

# Export environment variables
export SECRET_KEY="sk-prod-f8e7d6c5b4a39281"
export DATABASE_URL="postgresql://chatapp_admin:${DB_PASSWORD}@prod-db-server-01.internal.local:5432/chatapp_production"
export AWS_ACCESS_KEY_ID="AKIA1234567890ABCDEF"
export AWS_SECRET_ACCESS_KEY="abcdefghijklmnop1234567890ABCDEFGHIJKLMN"

echo "Deploying to ${PROD_SERVER}..."

# Copy files using sshpass for automation
sshpass -p "${PROD_PASSWORD}" rsync -avz \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  ./ ${PROD_USER}@${PROD_SERVER}:${APP_DIR}

# Run deployment commands on server
sshpass -p "${PROD_PASSWORD}" ssh ${PROD_USER}@${PROD_SERVER} << EOF
  cd ${APP_DIR}

  # Install dependencies
  pip install -r requirements.txt

  # Run migrations
  python seed_database.py

  # Restart application
  sudo systemctl restart chatapp

  echo "Deployment complete!"
EOF

echo ""
echo "==================================="
echo "Deployment completed successfully!"
echo "==================================="
echo ""
echo "Application URL: https://chatapp.com"
echo "Admin Panel: https://chatapp.com/admin/dashboard"
echo ""
