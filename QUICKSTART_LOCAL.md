# WorkSphere HR — Local Quick Start Guide

## Prerequisites
- Docker Desktop running
- Docker Compose v2+

## Start the Application

```bash
# 1. Navigate to the project folder
cd worksphere_fixed

# 2. Build and start all services (first run takes ~3-5 min to build)
docker compose up --build -d

# 3. Watch Django logs until you see "WorkSphere HR starting up"
docker compose logs -f django
# Wait until you see: "Booting worker with pid" — then the app is ready.

# 4. Open your browser
http://localhost        # via Nginx (recommended)
http://localhost:8000   # via Nginx port 8000 passthrough
```

## Login Credentials

| Role         | Email                     | Password   | Access |
|--------------|---------------------------|------------|--------|
| Super Admin  | admin@worksphere.hr       | Admin@123  | Full access + Django Admin |
| HR Admin     | hr@worksphere.hr          | Admin@123  | HR Dashboard, all modules |
| Payroll Admin| payroll@worksphere.hr     | Pay@123    | Payroll modules |
| Manager      | manager@worksphere.hr     | Mgr@123    | Manager Dashboard, team |
| Employee     | employee@worksphere.hr    | Emp@123    | Employee Dashboard |

## Key URLs (all via http://localhost)

| Page                  | URL                        |
|-----------------------|---------------------------|
| Login                 | /auth/login/               |
| Dashboard (auto-role) | /                          |
| Attendance            | /attendance/               |
| Clock In/Out          | /attendance/clock/         |
| My Leave              | /leave/                    |
| Apply Leave           | /leave/apply/              |
| Leave Requests        | /leave/requests/           |
| My Payslips           | /payroll/my-payslips/      |
| Payroll Admin         | /payroll/                  |
| Employee Directory    | /employees/                |
| Reports               | /reports/                  |
| Django Admin          | /admin/                    |
| API Docs (Swagger)    | /api/docs/                 |
| Flower (Celery)       | http://localhost:5555      |

## Useful Commands

```bash
# View all service logs
docker compose logs -f

# View only Django logs
docker compose logs -f django

# Restart just Django (after code changes)
docker compose restart django

# Stop everything
docker compose down

# Stop and remove all data (fresh start)
docker compose down -v

# Run Django management commands
docker compose exec django python manage.py shell
docker compose exec django python manage.py create_demo_data
```

## Troubleshooting

**"WorkSphere HR is starting up..." page keeps showing**
- Wait 60 seconds — Django needs to run migrations and seed demo data on first boot
- Check logs: `docker compose logs django`

**Login page shows but login fails**
- Make sure cookies are enabled in your browser
- Try http://localhost (port 80) instead of direct port 8000

**502 Bad Gateway**
- Django container may still be starting. Wait and refresh.
- Check: `docker compose ps` — all containers should be "Up"

**Database errors**
- Fresh start: `docker compose down -v && docker compose up --build -d`
