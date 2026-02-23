# Guide de Déploiement

## 📋 Prérequis

1. Compte **Supabase** (base de données PostgreSQL)
2. Compte **Twilio** avec WhatsApp Business API activé
3. Compte **Railway** (ou autre plateforme cloud)

---

## 🗄️ Étape 1 : Configuration Supabase

### 1.1 Créer un projet Supabase
1. Aller sur [supabase.com](https://supabase.com)
2. Créer un nouveau projet
3. Noter l'URL de connexion PostgreSQL

### 1.2 Récupérer l'URL de connexion
Format : `postgresql://user:password@host:port/database`

---

## 📱 Étape 2 : Configuration Twilio

### 2.1 Créer un compte Twilio
1. S'inscrire sur [twilio.com](https://www.twilio.com)
2. Activer WhatsApp Business API

### 2.2 Récupérer les credentials
- `TWILIO_ACCOUNT_SID`: Dans le dashboard Twilio
- `TWILIO_AUTH_TOKEN`: Dans le dashboard Twilio
- `TWILIO_WHATSAPP_NUMBER`: Numéro sandbox ou numéro acheté

### 2.3 Configuration du webhook (à faire après déploiement)
URL à configurer : `https://votre-app.railway.app/api/v1/webhook/whatsapp`

---

## 🚀 Étape 3 : Déploiement sur Railway

### 3.1 Installer Railway CLI (optionnel)
```bash
npm i -g @railway/cli
railway login
```

### 3.2 Déploiement via GitHub

1. **Pousser le code sur GitHub**
```bash
cd whatsapp-tracking-backend
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/votre-username/whatsapp-backend.git
git push -u origin main
```

2. **Connecter à Railway**
- Aller sur [railway.app](https://railway.app)
- "New Project" → "Deploy from GitHub repo"
- Sélectionner votre repository

3. **Configurer les variables d'environnement**

Dans Railway Settings → Variables :

```env
DATABASE_URL=postgresql://user:password@host:port/database
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
APP_ENV=production
DEBUG=False
API_SECRET_KEY=votre-cle-secrete-aleatoire-longue
MAX_AUTH_ATTEMPTS=3
SESSION_TIMEOUT_MINUTES=30
LOG_LEVEL=INFO
PORT=8000
```

4. **Déployer**
Railway va automatiquement :
- Installer les dépendances
- Lancer l'application
- Générer une URL publique

---

## 📊 Étape 4 : Initialiser la base de données

### 4.1 Créer les migrations
```bash
# Localement
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4.2 Import des données
```bash
python scripts/import_excel.py votre_fichier.xlsx
```

---

## 🔧 Étape 5 : Configuration Twilio Webhook

1. Aller dans Twilio Console
2. Messaging → Settings → WhatsApp Sandbox (ou votre numéro)
3. "When a message comes in" :
   - URL : `https://votre-app.railway.app/api/v1/webhook/whatsapp`
   - Méthode : `POST`
4. Sauvegarder

---

## ✅ Étape 6 : Tests

### 6.1 Vérifier la santé de l'API
```bash
curl https://votre-app.railway.app/api/v1/admin/health
```

### 6.2 Tester le webhook WhatsApp
1. Rejoindre le sandbox Twilio WhatsApp
2. Envoyer un message avec un numéro enregistré
3. Vérifier les logs Railway

---

## 📝 Commandes Utiles

### Logs en temps réel (Railway CLI)
```bash
railway logs
```

### Redémarrer l'application
```bash
railway up
```

### Accéder à la base de données
```bash
railway connect postgres
```

---

## 🔐 Sécurité Production

### À faire avant la mise en production :

1. **Générer une vraie clé secrète**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Restreindre CORS**
Dans `app/main.py`, modifier :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-domaine.com"],  # Pas "*"
    ...
)
```

3. **Activer la validation des signatures Twilio**
Dans `app/routes/webhook.py`, décommenter la validation.

4. **Configurer les sauvegardes DB**
Activer les sauvegardes automatiques dans Supabase.

---

## 🐛 Dépannage

### L'application ne démarre pas
- Vérifier les logs : `railway logs`
- Vérifier que toutes les variables d'environnement sont définies

### Base de données inaccessible
- Vérifier l'URL de connexion Supabase
- Vérifier que le projet Supabase est actif
- Tester la connexion depuis un autre client

### Webhook ne reçoit pas les messages
- Vérifier l'URL dans Twilio Console
- Vérifier que l'app est accessible publiquement
- Regarder les logs Railway pendant l'envoi d'un message

---

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)
- [Documentation Supabase](https://supabase.com/docs)
- [Documentation Railway](https://docs.railway.app/)
