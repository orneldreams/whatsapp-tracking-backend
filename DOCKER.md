# Docker Setup Guide

## Quick Start

### Build and Run with Docker Compose

```bash
# Using default environment variables (.env.docker)
docker-compose up -d

# Or with custom environment file
docker-compose --env-file .env.production up -d
```

### Build Image Manually

```bash
# Build the image
docker build -t whatsapp-tracking-backend:latest .

# Run the container
docker run -d \
  --name whatsapp-backend \
  -p 8000:8000 \
  --env-file .env.docker \
  -v $(pwd)/whatsapp_tracking.db:/app/whatsapp_tracking.db \
  whatsapp-tracking-backend:latest
```

## Configuration

### Environment Variables

Edit `.env.docker` before running:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
WEBHOOK_URL=https://your-domain.com/api/v1/webhook/whatsapp
```

### Volumes

- **Database**: `./whatsapp_tracking.db:/app/whatsapp_tracking.db` - Persist database between restarts
- **Logs**: `./logs:/app/logs` - Application logs

## Useful Commands

### View Logs

```bash
docker-compose logs -f whatsapp-backend
```

### Stop Container

```bash
docker-compose down
```

### Access Container Shell

```bash
docker-compose exec whatsapp-backend /bin/bash
```

### Rebuild Image

```bash
docker-compose build --no-cache
```

### Check Health

```bash
docker-compose exec whatsapp-backend curl http://localhost:8000/health
```

## Deployment

For production deployment on Railway.app:

1. Railway will automatically detect and build from Dockerfile
2. Set environment variables in Railway dashboard
3. Database persists via volumes

## Troubleshooting

**Port already in use:**
```bash
docker-compose down
# Change port in docker-compose.yml if needed
docker-compose up -d
```

**Database issues:**
```bash
# Remove volume and start fresh
docker-compose down -v
docker-compose up -d
```

**Check container status:**
```bash
docker ps
docker-compose ps
```
