# Documentation API

## Endpoints Disponibles

### 🔗 Webhook WhatsApp

#### POST `/api/v1/webhook/whatsapp`
Reçoit les messages WhatsApp de Twilio.

**Paramètres Form:**
- `From`: Numéro WhatsApp de l'expéditeur
- `To`: Numéro WhatsApp de destination
- `Body`: Contenu du message
- `MessageSid`: ID du message Twilio

**Réponse:**
```json
{
  "status": "tracked|authenticating|rejected",
  "authenticated": true|false
}
```

---

### 👥 Personnes

#### GET `/api/v1/persons/`
Liste toutes les personnes.

**Query Params:**
- `skip`: Offset (défaut: 0)
- `limit`: Nombre max de résultats (défaut: 100)

**Réponse:**
```json
[
  {
    "id": 1,
    "phone_number": "+33612345678",
    "identifiant_interne": "ABC123",
    "date_cle": "2024-01-15T00:00:00",
    "localite": "Paris",
    "numero_referent": "REF001",
    "verified": true,
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean@example.com",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-10T15:30:00",
    "last_activity": "2024-01-10T15:30:00"
  }
]
```

#### GET `/api/v1/persons/{person_id}`
Récupère une personne par ID.

#### GET `/api/v1/persons/phone/{phone_number}`
Récupère une personne par numéro de téléphone.

#### POST `/api/v1/persons/`
Crée une nouvelle personne.

**Body:**
```json
{
  "phone_number": "+33612345678",
  "identifiant_interne": "ABC123",
  "date_cle": "2024-01-15T00:00:00",
  "localite": "Paris",
  "numero_referent": "REF001",
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean@example.com"
}
```

#### PUT `/api/v1/persons/{person_id}`
Met à jour une personne.

---

### 💬 Messages

#### GET `/api/v1/messages/{phone_number}`
Récupère les messages d'une personne.

**Query Params:**
- `skip`: Offset (défaut: 0)
- `limit`: Nombre max de résultats (défaut: 50)

**Réponse:**
```json
[
  {
    "id": 1,
    "phone_number": "+33612345678",
    "content": "Mon message",
    "message_type": "tracking",
    "twilio_message_sid": "SM123...",
    "direction": "inbound",
    "created_at": "2024-01-10T15:30:00",
    "sent_at": "2024-01-10T15:30:00"
  }
]
```

#### GET `/api/v1/messages/sid/{message_sid}`
Récupère un message par son SID Twilio.

---

### ⚙️ Administration

#### GET `/api/v1/admin/health`
Vérifie la santé de l'application.

**Réponse:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-10T15:30:00",
  "database": "ok",
  "service": "whatsapp-tracking-backend"
}
```

#### GET `/api/v1/admin/stats`
Statistiques d'utilisation.

**Réponse:**
```json
{
  "total_persons": 150,
  "verified_persons": 120,
  "unverified_persons": 30,
  "total_messages": 1250,
  "active_auth_sessions": 3
}
```

---

## Flux d'Authentification

### 1. Premier message
L'utilisateur envoie un message WhatsApp → Le système vérifie s'il existe dans la base.

### 2. Si non vérifié
Le système envoie la première question d'authentification.

### 3. Questions successives
L'utilisateur répond aux 3 questions :
1. Identifiant interne
2. Localité
3. Numéro de référent

### 4. Validation
- Si toutes les réponses sont correctes → Personne vérifiée
- Si une réponse est incorrecte → Nouvelle tentative (max 3)
- Si 3 tentatives échouées → Session rejetée

### 5. Après vérification
Tous les messages sont enregistrés comme messages de suivi.

---

## Codes d'Erreur

- `400` - Requête invalide
- `404` - Ressource non trouvée
- `500` - Erreur serveur

---

## Configuration Twilio

### Webhook URL
Configurer dans Twilio Console :
```
https://votre-domaine.railway.app/api/v1/webhook/whatsapp
```

**Méthode:** POST

**Content-Type:** application/x-www-form-urlencoded

---

## Variables d'Environnement

Voir `.env.example` pour la liste complète des variables requises.

**Obligatoires:**
- `DATABASE_URL`: URL PostgreSQL (Supabase)
- `TWILIO_ACCOUNT_SID`: SID du compte Twilio
- `TWILIO_AUTH_TOKEN`: Token d'authentification Twilio
- `TWILIO_WHATSAPP_NUMBER`: Numéro WhatsApp Twilio (format: whatsapp:+14155238886)
- `API_SECRET_KEY`: Clé secrète pour l'application
