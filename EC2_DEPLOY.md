# WorkSphere HR — EC2 Deployment Guide
# EC2 Public IP: 3.107.228.172

## Step 1 — SSH into your EC2 instance
ssh -i your-key.pem ubuntu@3.107.228.172
# or for Amazon Linux:
# ssh -i your-key.pem ec2-user@3.107.228.172

## Step 2 — Install Docker + Compose V2
# Ubuntu:
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu    # or ec2-user for Amazon Linux
newgrp docker                      # Apply group without logout

# Verify:
docker --version
docker compose version             # Must show v2.x.x

## Step 3 — Upload your project files
# From your LOCAL machine:
scp -i your-key.pem -r worksphere_hr/ ubuntu@3.107.228.172:~/

## Step 4 — On EC2: Setup .env
cd ~/worksphere_hr
cp .env.ec2 .env                   # Use the EC2-specific env file

## Step 5 — Open Security Group ports in AWS Console
# Go to EC2 → Security Groups → Inbound Rules → Add:
#   Port 80   (HTTP)    — 0.0.0.0/0
#   Port 8000 (Django)  — 0.0.0.0/0
#   Port 5555 (Flower)  — Your IP only (optional)
#   Port 22   (SSH)     — Your IP

## Step 6 — Build and run
docker compose -f docker-compose.ec2.yml up --build -d

# Watch logs:
docker compose -f docker-compose.ec2.yml logs -f django

## Step 7 — Access the app
# Main app:   http://3.107.228.172
# Alt port:   http://3.107.228.172:8000
# API Docs:   http://3.107.228.172/api/docs/
# Admin:      http://3.107.228.172/admin/
# Flower:     http://3.107.228.172:5555

## Useful commands
# Stop all:
docker compose -f docker-compose.ec2.yml down

# Rebuild one service:
docker compose -f docker-compose.ec2.yml up --build -d django

# View logs:
docker compose -f docker-compose.ec2.yml logs -f

# Django shell:
docker compose -f docker-compose.ec2.yml exec django python manage.py shell

# Create superuser manually:
docker compose -f docker-compose.ec2.yml exec django python manage.py createsuperuser
