# WorkSphere HR - Quick Start

## Local Machine (Windows/Mac/Linux)

```bash
# 1. Extract the zip
# 2. Open terminal in the worksphere_fixed folder
# 3. Run:
docker compose up --build -d

# 4. Wait 60-90 seconds, then open:
#    http://localhost:8000
#    Login: admin@worksphere.hr / Admin@123
```

## EC2 Ubuntu Instance

```bash
# 1. Upload project to EC2
scp -i your-key.pem -r worksphere_fixed/ ubuntu@3.107.228.172:~/

# 2. SSH into EC2
ssh -i your-key.pem ubuntu@3.107.228.172

# 3. Run deploy script (installs Docker, clears old volumes, starts app)
cd worksphere_fixed
chmod +x deploy.sh
./deploy.sh

# 4. Open in browser:
#    http://3.107.228.172
#    http://3.107.228.172:8000
```

## ⚠️ If you already ran it before and get migration errors:

```bash
# Stop everything and remove old database volumes
docker compose down
docker volume rm $(docker volume ls -q | grep postgres)
docker compose up --build -d
```

## Credentials
| Role       | Email                       | Password  |
|------------|-----------------------------|-----------|
| Super Admin| admin@worksphere.hr         | Admin@123 |
| HR Admin   | hr@worksphere.hr            | Admin@123 |
| Manager    | manager@worksphere.hr       | Mgr@123   |
| Employee   | employee@worksphere.hr      | Emp@123   |

## URLs
- App:      http://localhost:8000
- Admin:    http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/
- Flower:   http://localhost:5555 (admin/flower123)
