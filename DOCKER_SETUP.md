# DiagnoPet Docker Setup Guide

## Local Development (No Nginx)

### Quick Start for Testing

#### 1. Copy environment variables
```bash
cp .env.example .env
```
Update `.env` with your Supabase credentials.

#### 2. Start single container
```bash
docker-compose -f docker-compose.local.yml up
```

This starts:
- **1x Uvicorn App Container** on port 8000
- Uses your **Supabase remote database**

#### 3. Run migrations
```bash
docker-compose -f docker-compose.local.yml exec app alembic upgrade head
```

#### 4. Access the application
```
http://localhost:8000
```

API docs: `http://localhost:8000/api/v1/docs`

---

## Get Supabase Connection String

1. Go to your Supabase project dashboard
2. Click **Settings** → **Database**
3. Copy the **Connection string** (URI format)
4. Replace values in `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres
   ```

---

## Production Setup (With Nginx + Load Balancing)

### 1. Copy environment variables
```bash
cp .env.example .env
```
Update with your production credentials.

### 2. Build and start all containers
```bash
docker-compose up -d
```

This starts:
- **Nginx** (port 80) - Load balancer
- **3x Uvicorn App Containers** - Each on port 8000 internally
- Connects to **Supabase remote database**

### 3. Run migrations
```bash
docker-compose exec app1 alembic upgrade head
```

### 4. Access the application
```
http://localhost
```

API docs: `http://localhost/api/v1/docs`

---

## Architecture

### Local Development
```
Client
  ↓
http://localhost:8000
  ↓
Uvicorn (1 container)
  ↓
Supabase PostgreSQL (remote)
```

### Production
```
Client Requests (http://localhost)
        ↓
    Nginx (Port 80)
    Load Balancer
        ↓
    ┌─────────────────────┐
    │   least_conn LB     │
    └─────────────────────┘
        ↓ ↓ ↓
    ┌──────┴──────┬──────┐
    ↓             ↓      ↓
 app1:8000    app2:8000  app3:8000
(Uvicorn)    (Uvicorn)  (Uvicorn)
    ↓             ↓      ↓
    └──────┬──────┴──────┘
           ↓
    Supabase PostgreSQL (remote)
```

---

## Common Commands

### Local Dev
```bash
# Start
docker-compose -f docker-compose.local.yml up

# Stop
docker-compose -f docker-compose.local.yml down

# View logs
docker-compose -f docker-compose.local.yml logs -f app

# Rebuild image
docker-compose -f docker-compose.local.yml build --no-cache
```

### Production
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f nginx
docker-compose logs -f app1

# Restart single app
docker-compose restart app1
```

---

## Environment Variables Needed

```env
# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres

# Security
SECRET_KEY=your-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio (optional for SMS)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Supabase (optional for storage)
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## Production Load Balancing Details

- **Algorithm**: `least_conn` - Distributes to server with fewest active connections
- **Max fails**: 3 consecutive failures mark container as down
- **Fail timeout**: 30 seconds before retry
- **Client max body size**: 50MB (for file uploads)

---

## Troubleshooting

### Connection refused to database
- Verify Supabase project is running
- Check `DATABASE_URL` format in `.env`
- Test connection: `docker-compose -f docker-compose.local.yml exec app psql $DATABASE_URL`

### Migrations not applying
```bash
docker-compose -f docker-compose.local.yml exec app alembic current
docker-compose -f docker-compose.local.yml exec app alembic history
```

### Container crashes
```bash
# View detailed logs
docker-compose -f docker-compose.local.yml logs app

# Rebuild and restart
docker-compose -f docker-compose.local.yml up --build
```

### Port already in use
```bash
lsof -i :8000
kill -9 <PID>
```

---

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure HTTPS (SSL certificate in nginx.conf)
- [ ] Use managed Supabase database (already remote)
- [ ] Set proper CORS origins in main.py
- [ ] Configure Twilio and Supabase credentials
- [ ] Scale to 3+ containers
- [ ] Set up log aggregation
- [ ] Monitor container health
- [ ] Configure CI/CD pipeline
