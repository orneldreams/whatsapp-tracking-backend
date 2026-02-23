# Railway.app Configuration Guide

## Overview

Cette application est containerisée et prête pour deployment sur Railway.app. Ce guide vous montre comment configurer les variables d'environnement nécessaires.

## Step 1: Create Railway Project

1. Allez sur [railway.app](https://railway.app)
2. Connectez-vous avec GitHub
3. Créez un nouveau projet et sélectionnez ce repo GitHub: `orneldreams/whatsapp-tracking-backend`

## Step 2: Add Environment Variables

Railway va déployer automatiquement une fois le repo sélectionné. Mais il va crasher car les variables d'environnement manquent.

### Variables Requises

Allez dans le dashboard Railway → Variables → Ajouter:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
DATABASE_URL=sqlite:///./whatsapp_tracking.db
API_SECRET_KEY=your-super-secret-key-for-production
```

### Variables Optionnelles (avec valeurs par défaut)

Ces variables ne sont pas obligatoires et ont des valeurs par défaut:

```
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
MAX_AUTH_ATTEMPTS=3
SESSION_TIMEOUT_MINUTES=30
```

## Step 3: Deploy

### Option A: Auto-Deploy (Recommandé)

1. Une fois les variables ajoutées dans Railway
2. Cliquez **Redeploy** dans le dashboard
3. Railway va:
   - Cloner le repo
   - Construire l'image Docker avec le Dockerfile
   - Lancer le container avec vos variables d'environnement
   - Vous donner une URL publique

### Option B: Manual Deploy

```bash
# Si vous avez le CLI Railway installé
railway login
railway link <your-project-id>
railway up
```

## Step 4: Verify Deployment

Une fois déployé, vérifiez que tout fonctionne:

```bash
# Health check
curl https://yourapp.railway.app/health

# Vous devriez voir:
{"status": "healthy"}
```

## Step 5: Configure Twilio Webhook

Maintenant que Railway vous a donné une URL publique (ex: `https://whatsapp-tracking-backend.railway.app`):

1. Allez dans [Twilio Console](https://console.twilio.com)
2. Allez à **Messaging > WhatsApp Sandbox Settings**
3. Changez le champ "When a message comes in" vers:
   ```
   https://yourrailwayapp.railway.app/api/v1/webhook/whatsapp
   ```
4. Sauvegardez

## Troubleshooting

### Erreur: "Field required"

**Problème**: Les variables d'environnement ne sont pas définies dans Railway

**Solution**:
1. Allez dans Railway Dashboard
2. Cliquez sur votre projet
3. Allez dans "Variables"
4. Vérifiez que `TWILIO_ACCOUNT_SID` et `TWILIO_AUTH_TOKEN` sont définis
5. Cliquez "Redeploy"

### Erreur: "Connection refused"

**Problème**: Le container n'a pas pu démarrer

**Solution**:
1. Cliquez "View Logs" dans Railway
2. Cherchez les erreurs au début
3. Vérifiez les variables d'environnement

### Erreur: "Port already in use"

Ne devrait pas se produire avec Railway, mais si c'est le cas:
1. Railway gère automatiquement les ports
2. Ne mettez PAS de PORT dans les variables (c'est automatique sur Railway)

## Database Persistence

Par défaut, cette app utilise SQLite (`whatsapp_tracking.db`).

Sur Railway:
- ✅ La base de données persiste entre les deploys
- ✅ Les fichiers sont stockés dans le container persistent

Si vous voulez une vraie base de données persistante (PostgreSQL):
1. Créez une PostgreSQL instance dans Railway
2. Railway vous donnera une `DATABASE_URL`
3. Copiez-la dans vos variables d'environnement Railway
4. Redéployez

## API Endpoints

Une fois déployé, voici les endpoints disponibles:

### Health Check
```
GET /health
```

### Webhook WhatsApp
```
POST /api/v1/webhook/whatsapp
```

### Gestion des Personnes
```
GET /api/v1/persons/
POST /api/v1/persons/
GET /api/v1/persons/{person_id}
```

### Messages
```
GET /api/v1/messages/
GET /api/v1/messages/person/{person_id}
```

## Support

Pour plus d'aide:
- [Railway Docs](https://docs.railway.app)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
